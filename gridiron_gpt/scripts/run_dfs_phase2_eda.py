"""Run Phase 2 EDA and a simple leakage-safe DFS baseline.

Reads the processed QB/RB/WR/TE player-week table produced by
build_dfs_player_week_dataset.py. The baseline predicts current PPR fantasy
points from the player's prior three appearances.

Run from the repository's gridiron_gpt directory:

    python scripts/run_dfs_phase2_eda.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl

INPUT = Path("data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet")
REPORT_DIR = Path("data/dfs/reports")
BASELINE_CSV = REPORT_DIR / "dfs_phase2_baseline_metrics.csv"
SUMMARY_CSV = REPORT_DIR / "dfs_phase2_position_summary.csv"
EDA_JSON = REPORT_DIR / "dfs_phase2_eda_summary.json"

TARGET = "fantasy_points_ppr"
PREDICTION = "fantasy_points_ppr_roll3"


def metric_row(frame: pl.DataFrame, label: str) -> dict:
    errors = frame.select(
        (pl.col(PREDICTION) - pl.col(TARGET)).alias("error")
    )
    mae = errors.select(pl.col("error").abs().mean()).item()
    mse = errors.select((pl.col("error") ** 2).mean()).item()
    rmse = math.sqrt(mse) if mse is not None else None
    return {
        "group": label,
        "rows": frame.height,
        "mae": mae,
        "rmse": rmse,
    }


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(
            f"Missing {INPUT}. Run scripts/build_dfs_player_week_dataset.py first."
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = pl.read_parquet(INPUT)

    required = {
        "position_group", "season", "split", "has_prior_game",
        TARGET, PREDICTION, "targets", "carries", "receptions",
    }
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError("Missing required fields: " + ", ".join(sorted(missing)))

    # Baseline evaluation requires at least one prior appearance. The roll3
    # feature itself is already shifted, so the current game's outcome is not
    # included in its prediction.
    baseline = df.filter(
        pl.col("has_prior_game")
        & pl.col(PREDICTION).is_not_null()
        & pl.col(TARGET).is_not_null()
    )

    metrics = [metric_row(baseline, "ALL")]
    for position in ["QB", "RB", "WR", "TE"]:
        metrics.append(
            metric_row(
                baseline.filter(pl.col("position_group") == position),
                position,
            )
        )
    metrics_df = pl.DataFrame(metrics)
    metrics_df.write_csv(BASELINE_CSV)

    position_summary = (
        df.group_by("position_group")
        .agg(
            pl.len().alias("rows"),
            pl.col(TARGET).mean().alias("mean_ppr_points"),
            pl.col(TARGET).median().alias("median_ppr_points"),
            pl.col(TARGET).std().alias("std_ppr_points"),
            pl.col(TARGET).min().alias("min_ppr_points"),
            pl.col(TARGET).max().alias("max_ppr_points"),
            pl.col("targets").mean().alias("mean_targets"),
            pl.col("carries").mean().alias("mean_carries"),
            pl.col("receptions").mean().alias("mean_receptions"),
            pl.col("has_prior_game").sum().alias("baseline_ready_rows"),
        )
        .sort("position_group")
    )
    position_summary.write_csv(SUMMARY_CSV)

    split_counts = {
        str(row["split"]): row["len"]
        for row in df.group_by("split").len().sort("split").to_dicts()
    }
    season_counts = {
        str(row["season"]): row["len"]
        for row in df.group_by("season").len().sort("season").to_dicts()
    }

    summary = {
        "input": str(INPUT),
        "rows": df.height,
        "target": TARGET,
        "baseline_prediction": PREDICTION,
        "baseline_definition": "mean PPR fantasy points over up to the previous 3 player appearances within the same season; current game shifted out",
        "baseline_rows": baseline.height,
        "cold_start_rows": df.filter(~pl.col("has_prior_game")).height,
        "season_counts": season_counts,
        "split_counts": split_counts,
        "baseline_metrics": metrics,
        "position_summary": position_summary.to_dicts(),
    }
    EDA_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("DFS Phase 2 EDA / baseline complete")
    print(f"Offensive rows: {df.height:,}")
    print(f"Baseline evaluation rows: {baseline.height:,}")
    print(f"Cold-start rows retained: {summary['cold_start_rows']:,}")
    print()
    print("3-game rolling PPR baseline")
    print(metrics_df)
    print()
    print("Position summary")
    print(position_summary)
    print()
    print(f"Metrics CSV: {BASELINE_CSV}")
    print(f"Position summary CSV: {SUMMARY_CSV}")
    print(f"EDA JSON: {EDA_JSON}")


if __name__ == "__main__":
    main()
