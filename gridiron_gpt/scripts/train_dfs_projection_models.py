"""Train and evaluate Phase 3 DFS fantasy-point projection models."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_PATH = Path(
    "data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet"
)
OUTPUT_DIR = Path("data/dfs/models/phase3")
TARGET = "fantasy_points_ppr"
RANDOM_STATE = 42

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

NUMERIC_FEATURES = HISTORICAL_FEATURES + ["week", "has_prior_game"]
CATEGORICAL_FEATURES = ["position"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def make_pipeline(estimator):
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            )
        ]
    )

    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
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
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    VALID_POSITIONS = ["QB", "RB", "WR", "TE"]
    df = df.loc[df["position"].isin(VALID_POSITIONS)].copy()

    missing = sorted(set(FEATURES + [TARGET, "season"]) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    train = df[df["season"].between(2020, 2023)].copy()
    validation = df[df["season"] == 2024].copy()
    test = df[df["season"] == 2025].copy()

    print("DATA SPLITS")
    print(f"Train:      {len(train):,}")
    print(f"Validation: {len(validation):,}")
    print(f"Test:       {len(test):,}")

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_val = validation[FEATURES]
    y_val = validation[TARGET]

    models = {
        "ridge": Ridge(alpha=10.0),
        "random_forest": RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "gradient_boosting": HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.05,
            max_leaf_nodes=31,
            random_state=RANDOM_STATE,
        ),
    }

    results = []

    baseline_predictions = validation["fantasy_points_ppr_roll3"]
    baseline_mask = baseline_predictions.notna()

    baseline_metrics = calculate_metrics(
        y_val[baseline_mask],
        baseline_predictions[baseline_mask],
    )

    print("\n2024 ROLLING BASELINE")
    print(baseline_metrics)

    for name, estimator in models.items():
        print(f"\nTraining {name}...")

        pipeline = make_pipeline(estimator)
        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_val)
        metrics = calculate_metrics(y_val, predictions)

        results.append(
            {
                "model": name,
                "validation_rows": len(validation),
                **metrics,
            }
        )

        artifact_path = OUTPUT_DIR / f"{name}.joblib"
        joblib.dump(pipeline, artifact_path)

        print(
            f"{name}: MAE={metrics['mae']:.4f}, "
            f"RMSE={metrics['rmse']:.4f}"
        )
        print(f"Saved: {artifact_path}")

    results_df = pd.DataFrame(results).sort_values("mae")
    results_df.to_csv(OUTPUT_DIR / "validation_metrics.csv", index=False)

    config = {
        "target": TARGET,
        "features": FEATURES,
        "train_seasons": [2020, 2021, 2022, 2023],
        "validation_season": 2024,
        "test_season": 2025,
        "baseline_validation_metrics": baseline_metrics,
        "random_state": RANDOM_STATE,
    }

    with open(OUTPUT_DIR / "training_config.json", "w") as file:
        json.dump(config, file, indent=2)

    print("\nMODEL COMPARISON")
    print(results_df.to_string(index=False))

    print("\n2025 test data remains untouched.")
    print("Initial Phase 3 training complete.")


if __name__ == "__main__":
    main()
