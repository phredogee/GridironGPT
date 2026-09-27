"""Audit the Phase 2 Week 5 preprocessed DFS dataset.

Checks split integrity, feature missingness, finite numeric values, cold-start
handling, and leakage-safe feature structure before Week 5 is declared
complete.

Run from the repository's gridiron_gpt directory:

    python scripts/audit_dfs_phase2_week5.py
"""
from __future__ import annotations

import json
from pathlib import Path

import polars as pl

INPUT = Path("data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet")
REPORT = Path("data/dfs/reports/dfs_phase2_week5_audit.json")

FEATURE_SUFFIXES = ("_lag1", "_roll3", "_roll5")
EXPECTED_SPLITS = {
    "train": {2020, 2021, 2022, 2023},
    "validation": {2024},
    "test": {2025},
}


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(
            f"Missing {INPUT}. Run scripts/build_dfs_player_week_dataset.py first."
        )

    df = pl.read_parquet(INPUT)
    feature_cols = [c for c in df.columns if c.endswith(FEATURE_SUFFIXES)]

    duplicate_keys = (
        df.group_by(["season", "week", "game_id", "player_id"])
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    split_counts = {
        str(row["split"]): row["len"]
        for row in df.group_by("split").len().sort("split").to_dicts()
    }
    split_seasons = {
        split: sorted(
            df.filter(pl.col("split") == split)["season"].unique().to_list()
        )
        for split in EXPECTED_SPLITS
    }
    split_integrity = {
        split: set(split_seasons[split]) == seasons
        for split, seasons in EXPECTED_SPLITS.items()
    }

    missingness = []
    for col in feature_cols:
        nulls = df[col].null_count()
        missingness.append(
            {
                "feature": col,
                "null_rows": nulls,
                "null_pct": round((nulls / df.height) * 100, 4),
            }
        )

    # Feature columns are floating-point rolling/lag values. Count NaN and
    # infinite values separately from expected nulls caused by cold starts.
    numeric_anomalies = []
    for col in feature_cols:
        dtype = df.schema[col]
        if dtype in (pl.Float32, pl.Float64):
            nan_count = df.select(pl.col(col).is_nan().sum()).item()
            inf_count = df.select(pl.col(col).is_infinite().sum()).item()
            if nan_count or inf_count:
                numeric_anomalies.append(
                    {"feature": col, "nan_rows": nan_count, "infinite_rows": inf_count}
                )

    cold = df.filter(~pl.col("has_prior_game"))
    ready = df.filter(pl.col("has_prior_game"))

    cold_feature_non_null = {
        col: cold[col].len() - cold[col].null_count()
        for col in feature_cols
        if cold[col].len() - cold[col].null_count() > 0
    }

    ready_prediction_nulls = ready["fantasy_points_ppr_roll3"].null_count()

    report = {
        "input": str(INPUT),
        "rows": df.height,
        "columns": len(df.columns),
        "engineered_feature_columns": len(feature_cols),
        "duplicate_player_game_keys": duplicate_keys,
        "split_counts": split_counts,
        "split_seasons": split_seasons,
        "split_integrity": split_integrity,
        "cold_start_rows": cold.height,
        "baseline_ready_rows": ready.height,
        "baseline_ready_rows_missing_roll3_prediction": ready_prediction_nulls,
        "cold_start_feature_values_present": cold_feature_non_null,
        "feature_missingness": missingness,
        "numeric_anomalies": numeric_anomalies,
        "checks_passed": (
            duplicate_keys == 0
            and all(split_integrity.values())
            and ready_prediction_nulls == 0
            and not cold_feature_non_null
            and not numeric_anomalies
        ),
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("DFS Phase 2 Week 5 preprocessing audit")
    print(f"Rows: {df.height:,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Engineered lag/rolling features: {len(feature_cols)}")
    print(f"Duplicate player-game keys: {duplicate_keys}")
    print(f"Baseline-ready rows: {ready.height:,}")
    print(f"Cold-start rows: {cold.height:,}")
    print(f"Baseline-ready roll3 nulls: {ready_prediction_nulls:,}")
    print(f"Numeric anomalies: {len(numeric_anomalies)}")
    print("Split counts:")
    for split, count in split_counts.items():
        print(f"  {split}: {count:,} -> seasons {split_seasons.get(split, [])}")
    print(f"CHECKS PASSED: {report['checks_passed']}")
    print(f"Audit report: {REPORT}")


if __name__ == "__main__":
    main()
