"""Evaluate Phase 3 DFS projection models on 2024 validation data.

Produces fair baseline comparisons, position-level results, cold-start
analysis, and prediction files. Does not access the 2025 test split.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA_PATH = Path(
    "data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet"
)
MODEL_DIR = Path("data/dfs/models/phase3")
OUTPUT_DIR = MODEL_DIR / "evaluation"

TARGET = "fantasy_points_ppr"
BASELINE = "fantasy_points_ppr_roll3"

MODELS = {
    "ridge": MODEL_DIR / "ridge.joblib",
    "random_forest": MODEL_DIR / "random_forest.joblib",
    "gradient_boosting": MODEL_DIR / "gradient_boosting.joblib",
}


def calculate_metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    errors = predicted - actual

    return {
        "rows": len(actual),
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "bias": float(np.mean(errors)),
        "median_absolute_error": float(np.median(np.abs(errors))),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    VALID_POSITIONS = ["QB", "RB", "WR", "TE"]
    df = df.loc[df["position"].isin(VALID_POSITIONS)].copy()

    # Phase 3 development uses 2024 validation data only.
    validation = df.loc[df["season"] == 2024].copy()

    if validation.empty:
        raise ValueError("No 2024 validation rows found.")

    validation = validation.reset_index(drop=True)

    required = {
        TARGET,
        BASELINE,
        "position",
        "player_id",
        "season",
        "week",
        "has_prior_game",
    }

    missing = required - set(validation.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    predictions = validation[
        [
            "player_id",
            "player_name",
            "position",
            "season",
            "week",
            "has_prior_game",
            TARGET,
            BASELINE,
        ]
    ].copy()

    predictions = predictions.rename(
        columns={
            TARGET: "actual_ppr",
            BASELINE: "baseline_prediction",
        }
    )

    for name, model_path in MODELS.items():
        print(f"Loading {name}...")

        model = joblib.load(model_path)

        # Use exactly the feature columns saved in the fitted pipeline.
        features = list(model.feature_names_in_)

        predictions[name] = model.predict(validation[features])

    baseline_eligible = predictions["baseline_prediction"].notna()
    cold_start = ~baseline_eligible

    results = []

    def add_result(group, model_name, subset, prediction_column):
        if subset.empty:
            return

        metrics = calculate_metrics(
            subset["actual_ppr"],
            subset[prediction_column],
        )

        results.append(
            {
                "group": group,
                "model": model_name,
                **metrics,
            }
        )

    # A. Fair comparison: every model on the same baseline-ready rows.
    baseline_rows = predictions.loc[baseline_eligible]

    add_result(
        "baseline_eligible",
        "rolling_baseline",
        baseline_rows,
        "baseline_prediction",
    )

    for name in MODELS:
        add_result("baseline_eligible", name, baseline_rows, name)

    # B. All validation observations: ML models only.
    for name in MODELS:
        add_result("all_players", name, predictions, name)

    # C. Cold-start observations: no rolling baseline available.
    cold_rows = predictions.loc[cold_start]

    for name in MODELS:
        add_result("cold_start", name, cold_rows, name)

    # D. Position-level performance on identical baseline-ready rows.
    for position in ["QB", "RB", "WR", "TE"]:
        subset = baseline_rows.loc[
            baseline_rows["position"] == position
        ]

        add_result(
            f"position_{position}",
            "rolling_baseline",
            subset,
            "baseline_prediction",
        )

        for name in MODELS:
            add_result(f"position_{position}", name, subset, name)

    results_df = pd.DataFrame(results)

    results_path = OUTPUT_DIR / "evaluation_metrics.csv"
    predictions_path = OUTPUT_DIR / "validation_predictions.csv"

    results_df.to_csv(results_path, index=False)
    predictions.to_csv(predictions_path, index=False)

    print("\n" + "=" * 65)
    print("A. FAIR BASELINE COMPARISON — 2024")
    print("=" * 65)

    fair = results_df.loc[
        results_df["group"] == "baseline_eligible"
    ].sort_values("mae")

    print(
        fair[
            ["model", "rows", "mae", "rmse", "bias"]
        ].to_string(index=False)
    )

    print("\n" + "=" * 65)
    print("B. ALL PLAYERS — 2024")
    print("=" * 65)

    all_players = results_df.loc[
        results_df["group"] == "all_players"
    ].sort_values("mae")

    print(
        all_players[
            ["model", "rows", "mae", "rmse", "bias"]
        ].to_string(index=False)
    )

    print("\n" + "=" * 65)
    print("C. COLD-START PLAYERS — 2024")
    print("=" * 65)

    cold = results_df.loc[
        results_df["group"] == "cold_start"
    ].sort_values("mae")

    if cold.empty:
        print("No cold-start observations found.")
    else:
        print(
            cold[
                ["model", "rows", "mae", "rmse", "bias"]
            ].to_string(index=False)
        )

    print("\n" + "=" * 65)
    print("D. POSITION-SPECIFIC RESULTS — BASELINE-ELIGIBLE")
    print("=" * 65)

    position_results = results_df.loc[
        results_df["group"].str.startswith("position_")
    ]

    print(
        position_results[
            ["group", "model", "rows", "mae", "rmse"]
        ].to_string(index=False)
    )

    print("\nSaved evaluation files:")
    print(results_path)
    print(predictions_path)

    print("\n2025 test data was not evaluated.")


if __name__ == "__main__":
    main()
