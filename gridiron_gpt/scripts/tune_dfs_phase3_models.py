"""Tune DFS projection models using chronological validation.

Hyperparameters are selected using 2023 data. Selected models are
retrained on 2020-2023 and evaluated on 2024. The 2025 test set
is deliberately excluded.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import ParameterSampler


DATA_PATH = Path(
    "data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet"
)

OUTPUT_DIR = Path("data/dfs/models/phase3/tuning")
TARGET = "fantasy_points_ppr"
BASELINE = "fantasy_points_ppr_roll3"
RANDOM_STATE = 42
N_ITERATIONS = 12

HISTORICAL_FEATURES = [
    "fantasy_points_lag1",
    "fantasy_points_roll3",
    "fantasy_points_roll5",
    "fantasy_points_ppr_lag1",
    "fantasy_points_ppr_roll3",
    "fantasy_points_ppr_roll5",
    "targets_lag1",
    "targets_roll3",
    "targets_roll5",
    "carries_lag1",
    "carries_roll3",
    "carries_roll5",
    "receptions_lag1",
    "receptions_roll3",
    "receptions_roll5",
    "passing_yards_lag1",
    "passing_yards_roll3",
    "passing_yards_roll5",
    "rushing_yards_lag1",
    "rushing_yards_roll3",
    "rushing_yards_roll5",
    "receiving_yards_lag1",
    "receiving_yards_roll3",
    "receiving_yards_roll5",
    "target_share_lag1",
    "target_share_roll3",
    "target_share_roll5",
    "air_yards_share_lag1",
    "air_yards_share_roll3",
    "air_yards_share_roll5",
    "wopr_lag1",
    "wopr_roll3",
    "wopr_roll5",
]

NUMERIC_FEATURES = HISTORICAL_FEATURES + [
    "week",
    "has_prior_game",
]

CATEGORICAL_FEATURES = ["position"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def make_pipeline(estimator):
    numeric_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="constant", fill_value=0),
            ),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            )
        ]
    )

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_transformer,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("model", estimator),
        ]
    )


def calculate_metrics(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(
            np.sqrt(mean_squared_error(actual, predicted))
        ),
    }


def build_estimator(model_name, parameters):
    if model_name == "random_forest":
        return RandomForestRegressor(
            random_state=RANDOM_STATE,
            n_jobs=-1,
            **parameters,
        )

    if model_name == "gradient_boosting":
        return HistGradientBoostingRegressor(
            random_state=RANDOM_STATE,
            **parameters,
        )

    raise ValueError(f"Unknown model: {model_name}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    VALID_POSITIONS = ["QB", "RB", "WR", "TE"]
    df = df.loc[df["position"].isin(VALID_POSITIONS)].copy()

    required = set(FEATURES + [TARGET, BASELINE, "season"])
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing dataset columns: {sorted(missing)}"
        )

    internal_train = df.loc[
        df["season"].between(2020, 2022)
    ].copy()

    internal_validation = df.loc[
        df["season"] == 2023
    ].copy()

    final_train = df.loc[
        df["season"].between(2020, 2023)
    ].copy()

    validation_2024 = df.loc[
        df["season"] == 2024
    ].copy()

    print("CHRONOLOGICAL SPLITS")
    print(f"Internal training:   {len(internal_train):,}")
    print(f"Internal validation: {len(internal_validation):,}")
    print(f"Final training:      {len(final_train):,}")
    print(f"2024 validation:     {len(validation_2024):,}")
    print("2025: RESERVED — not loaded into model training")

    search_spaces = {
        "random_forest": {
            "n_estimators": [100, 200],
            "max_depth": [8, 12, 16],
            "min_samples_leaf": [3, 5, 10],
            "max_features": [0.7, 1.0],
        },
        "gradient_boosting": {
            "max_iter": [100, 200],
            "learning_rate": [0.03, 0.05, 0.1],
            "max_leaf_nodes": [15, 31],
            "l2_regularization": [0.0, 1.0],
        },
    }

    experiment_results = []
    final_results = []

    for model_name, search_space in search_spaces.items():
        print(f"\nTUNING {model_name.upper()}")

        candidates = list(
            ParameterSampler(
                search_space,
                n_iter=N_ITERATIONS,
                random_state=RANDOM_STATE,
            )
        )

        for iteration, parameters in enumerate(candidates, start=1):
            estimator = build_estimator(model_name, parameters)
            pipeline = make_pipeline(estimator)

            pipeline.fit(
                internal_train[FEATURES],
                internal_train[TARGET],
            )

            predictions = pipeline.predict(
                internal_validation[FEATURES]
            )

            metrics = calculate_metrics(
                internal_validation[TARGET],
                predictions,
            )

            experiment_results.append(
                {
                    "model": model_name,
                    "iteration": iteration,
                    "internal_mae": metrics["mae"],
                    "internal_rmse": metrics["rmse"],
                    "parameters": json.dumps(
                        parameters,
                        sort_keys=True,
                    ),
                }
            )

            print(
                f"Trial {iteration:02d}/{len(candidates)} "
                f"MAE={metrics['mae']:.4f} "
                f"RMSE={metrics['rmse']:.4f}"
            )

        model_experiments = [
            result
            for result in experiment_results
            if result["model"] == model_name
        ]

        best = min(
            model_experiments,
            key=lambda result: result["internal_mae"],
        )

        best_parameters = json.loads(best["parameters"])

        print("\nSelected parameters:")
        print(json.dumps(best_parameters, indent=2))

        final_pipeline = make_pipeline(
            build_estimator(model_name, best_parameters)
        )

        final_pipeline.fit(
            final_train[FEATURES],
            final_train[TARGET],
        )

        final_predictions = final_pipeline.predict(
            validation_2024[FEATURES]
        )

        # Compare on identical baseline-eligible observations.
        baseline_mask = (
            validation_2024[BASELINE].notna().to_numpy()
        )

        metrics = calculate_metrics(
            validation_2024[TARGET].to_numpy()[baseline_mask],
            final_predictions[baseline_mask],
        )

        final_results.append(
            {
                "model": model_name,
                "validation_rows": int(baseline_mask.sum()),
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "parameters": json.dumps(
                    best_parameters,
                    sort_keys=True,
                ),
            }
        )

        model_path = OUTPUT_DIR / f"{model_name}_tuned.joblib"
        joblib.dump(final_pipeline, model_path)

        print(
            f"\n2024 baseline-eligible: "
            f"MAE={metrics['mae']:.4f}, "
            f"RMSE={metrics['rmse']:.4f}"
        )
        print(f"Saved: {model_path}")

    experiments_df = pd.DataFrame(experiment_results)
    final_df = pd.DataFrame(final_results).sort_values("mae")

    experiments_df.to_csv(
        OUTPUT_DIR / "tuning_experiments.csv",
        index=False,
    )

    final_df.to_csv(
        OUTPUT_DIR / "tuned_validation_metrics.csv",
        index=False,
    )

    print("\n" + "=" * 65)
    print("TUNED MODEL COMPARISON — 2024")
    print("=" * 65)

    print(
        final_df[
            ["model", "validation_rows", "mae", "rmse"]
        ].to_string(index=False)
    )

    print("\nInitial untuned Random Forest MAE: 4.5691")
    print("Initial untuned Random Forest RMSE: 6.2495")
    print("\n2025 test data remains untouched.")


if __name__ == "__main__":
    main()