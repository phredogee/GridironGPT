"""Quantify Week 6 EDA patterns for the DFS Capstone.

This complements the visualization script with report-ready numeric evidence.
It measures usage/production relationships, baseline correlations and bias,
and season-level scoring summaries without changing the modeling dataset.

Run from the repository's gridiron_gpt directory:

    python scripts/analyze_dfs_phase2_patterns.py
"""
from __future__ import annotations

import json
from pathlib import Path

import polars as pl

INPUT = Path("data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet")
OUTPUT = Path("data/dfs/reports/dfs_phase2_pattern_analysis.json")
USAGE_CSV = Path("data/dfs/reports/dfs_phase2_usage_buckets.csv")
SEASON_CSV = Path("data/dfs/reports/dfs_phase2_season_summary.csv")

TARGET = "fantasy_points_ppr"
PREDICTION = "fantasy_points_ppr_roll3"


def corr(frame: pl.DataFrame, x: str, y: str) -> float | None:
    value = frame.select(pl.corr(x, y)).item()
    return None if value is None else float(value)


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(
            f"Missing {INPUT}. Run scripts/build_dfs_player_week_dataset.py first."
        )

    df = pl.read_parquet(INPUT)
    baseline = df.filter(
        pl.col("has_prior_game")
        & pl.col(PREDICTION).is_not_null()
        & pl.col(TARGET).is_not_null()
    )

    skill = df.filter(pl.col("position_group").is_in(["RB", "WR", "TE"])).with_columns(
        (pl.col("carries") + pl.col("targets")).alias("opportunities")
    )

    # Correlations describe association only; they are not interpreted as causal.
    usage_correlations = {
        "rb_wr_te_opportunities_vs_ppr": corr(skill, "opportunities", TARGET),
        "rb_wr_te_targets_vs_ppr": corr(skill, "targets", TARGET),
        "rb_wr_te_carries_vs_ppr": corr(skill, "carries", TARGET),
        "rb_wr_te_receptions_vs_ppr": corr(skill, "receptions", TARGET),
    }

    usage_buckets = (
        skill.with_columns(
            pl.when(pl.col("opportunities") <= 2).then(pl.lit("0-2"))
            .when(pl.col("opportunities") <= 5).then(pl.lit("3-5"))
            .when(pl.col("opportunities") <= 10).then(pl.lit("6-10"))
            .when(pl.col("opportunities") <= 15).then(pl.lit("11-15"))
            .when(pl.col("opportunities") <= 20).then(pl.lit("16-20"))
            .otherwise(pl.lit("21+"))
            .alias("opportunity_bucket")
        )
        .group_by("opportunity_bucket")
        .agg(
            pl.len().alias("rows"),
            pl.col(TARGET).mean().alias("mean_ppr_points"),
            pl.col(TARGET).median().alias("median_ppr_points"),
        )
        .with_columns(
            pl.col("opportunity_bucket")
            .replace_strict({"0-2": 0, "3-5": 1, "6-10": 2, "11-15": 3, "16-20": 4, "21+": 5})
            .alias("bucket_order")
        )
        .sort("bucket_order")
        .drop("bucket_order")
    )
    usage_buckets.write_csv(USAGE_CSV)

    baseline_with_error = baseline.with_columns(
        (pl.col(PREDICTION) - pl.col(TARGET)).alias("signed_error"),
        (pl.col(PREDICTION) - pl.col(TARGET)).abs().alias("absolute_error"),
    )

    baseline_patterns = {
        "actual_vs_predicted_correlation": corr(baseline, TARGET, PREDICTION),
        "mean_signed_error": float(baseline_with_error["signed_error"].mean()),
        "median_absolute_error": float(baseline_with_error["absolute_error"].median()),
    }

    by_position = []
    for position in ["QB", "RB", "WR", "TE"]:
        part = baseline_with_error.filter(pl.col("position_group") == position)
        by_position.append(
            {
                "position": position,
                "rows": part.height,
                "actual_vs_predicted_correlation": corr(part, TARGET, PREDICTION),
                "mean_signed_error": float(part["signed_error"].mean()),
                "median_absolute_error": float(part["absolute_error"].median()),
            }
        )

    season_summary = (
        df.group_by("season")
        .agg(
            pl.len().alias("rows"),
            pl.col(TARGET).mean().alias("mean_ppr_points"),
            pl.col(TARGET).median().alias("median_ppr_points"),
        )
        .sort("season")
    )
    season_summary.write_csv(SEASON_CSV)

    report = {
        "input": str(INPUT),
        "rows": df.height,
        "usage_population": "RB/WR/TE",
        "usage_note": "Opportunities are carries + targets. Correlations are descriptive associations, not causal effects.",
        "usage_correlations": usage_correlations,
        "usage_buckets": usage_buckets.to_dicts(),
        "baseline_patterns": baseline_patterns,
        "baseline_patterns_by_position": by_position,
        "season_summary": season_summary.to_dicts(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("DFS Phase 2 pattern analysis complete")
    print(f"Rows: {df.height:,}")
    print(f"Baseline rows: {baseline.height:,}")
    print()
    print("Usage correlations (RB/WR/TE)")
    for name, value in usage_correlations.items():
        print(f"  {name}: {value:.4f}" if value is not None else f"  {name}: null")
    print()
    print("Usage buckets")
    print(usage_buckets)
    print()
    print("Baseline patterns")
    print(f"  Actual/predicted correlation: {baseline_patterns['actual_vs_predicted_correlation']:.4f}")
    print(f"  Mean signed error: {baseline_patterns['mean_signed_error']:.4f}")
    print(f"  Median absolute error: {baseline_patterns['median_absolute_error']:.4f}")
    print()
    print("By position")
    for row in by_position:
        print(
            f"  {row['position']}: corr={row['actual_vs_predicted_correlation']:.4f}, "
            f"mean_signed_error={row['mean_signed_error']:.4f}, "
            f"median_abs_error={row['median_absolute_error']:.4f}"
        )
    print()
    print(f"JSON report: {OUTPUT}")
    print(f"Usage CSV: {USAGE_CSV}")
    print(f"Season CSV: {SEASON_CSV}")


if __name__ == "__main__":
    main()
