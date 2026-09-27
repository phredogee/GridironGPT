"""Run Phase 2 EDA, visualizations, and a leakage-safe DFS baseline.

Run from the repository's gridiron_gpt directory:

    python scripts/run_dfs_phase2_eda.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl

INPUT = Path("data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet")
REPORT_DIR = Path("data/dfs/reports")
FIGURE_DIR = REPORT_DIR / "figures"
BASELINE_CSV = REPORT_DIR / "dfs_phase2_baseline_metrics.csv"
SUMMARY_CSV = REPORT_DIR / "dfs_phase2_position_summary.csv"
EDA_JSON = REPORT_DIR / "dfs_phase2_eda_summary.json"

TARGET = "fantasy_points_ppr"
PREDICTION = "fantasy_points_ppr_roll3"
POSITIONS = ["QB", "RB", "WR", "TE"]


def metric_row(frame: pl.DataFrame, label: str) -> dict:
    errors = frame.select((pl.col(PREDICTION) - pl.col(TARGET)).alias("error"))
    mae = errors.select(pl.col("error").abs().mean()).item()
    mse = errors.select((pl.col("error") ** 2).mean()).item()
    return {
        "group": label,
        "rows": frame.height,
        "mae": mae,
        "rmse": math.sqrt(mse) if mse is not None else None,
    }


def save_distribution_chart(df: pl.DataFrame) -> Path:
    path = FIGURE_DIR / "ppr_distribution_by_position.png"
    data = [df.filter(pl.col("position_group") == p)[TARGET].to_list() for p in POSITIONS]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.boxplot(data, tick_labels=POSITIONS, showfliers=False)
    ax.set_title("PPR Fantasy-Point Distribution by Position")
    ax.set_xlabel("Position")
    ax.set_ylabel("PPR Fantasy Points")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def save_mean_points_chart(position_summary: pl.DataFrame) -> Path:
    path = FIGURE_DIR / "mean_ppr_points_by_position.png"
    ordered = position_summary.sort(
        pl.col("position_group").replace_strict({p: i for i, p in enumerate(POSITIONS)})
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(ordered["position_group"].to_list(), ordered["mean_ppr_points"].to_list())
    ax.set_title("Mean PPR Fantasy Points by Position")
    ax.set_xlabel("Position")
    ax.set_ylabel("Mean PPR Fantasy Points")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def save_baseline_error_chart(metrics_df: pl.DataFrame) -> Path:
    path = FIGURE_DIR / "baseline_error_by_position.png"
    position_metrics = metrics_df.filter(pl.col("group") != "ALL")
    ordered = position_metrics.sort(
        pl.col("group").replace_strict({p: i for i, p in enumerate(POSITIONS)})
    )
    x = list(range(len(POSITIONS)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([v - width / 2 for v in x], ordered["mae"].to_list(), width, label="MAE")
    ax.bar([v + width / 2 for v in x], ordered["rmse"].to_list(), width, label="RMSE")
    ax.set_xticks(x, POSITIONS)
    ax.set_title("3-Game Rolling Baseline Error by Position")
    ax.set_xlabel("Position")
    ax.set_ylabel("Fantasy Points")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def save_actual_vs_prediction_chart(baseline: pl.DataFrame) -> Path:
    path = FIGURE_DIR / "baseline_actual_vs_predicted.png"
    # Sample deterministically for a readable chart while metrics use all rows.
    sample = baseline.sort(["season", "week", "player_id"]).gather_every(10)
    actual = sample[TARGET].to_list()
    predicted = sample[PREDICTION].to_list()
    limit = max(max(actual, default=0), max(predicted, default=0))
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(actual, predicted, alpha=0.25, s=14)
    ax.plot([0, limit], [0, limit], linestyle="--", linewidth=1)
    ax.set_title("3-Game Baseline: Actual vs. Predicted PPR Points")
    ax.set_xlabel("Actual PPR Fantasy Points")
    ax.set_ylabel("Predicted PPR Fantasy Points")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def save_usage_chart(df: pl.DataFrame) -> Path:
    path = FIGURE_DIR / "usage_vs_ppr_points.png"
    # RB/WR/TE usage is summarized as opportunities = carries + targets.
    skill = df.filter(pl.col("position_group").is_in(["RB", "WR", "TE"]))
    usage = (
        skill.with_columns((pl.col("carries") + pl.col("targets")).alias("opportunities"))
        .group_by("opportunities")
        .agg(pl.len().alias("rows"), pl.col(TARGET).mean().alias("mean_ppr"))
        .filter((pl.col("rows") >= 25) & (pl.col("opportunities") <= 30))
        .sort("opportunities")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(usage["opportunities"].to_list(), usage["mean_ppr"].to_list())
    ax.set_title("Average PPR Points vs. Weekly Opportunities (RB/WR/TE)")
    ax.set_xlabel("Carries + Targets")
    ax.set_ylabel("Mean PPR Fantasy Points")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing {INPUT}. Run scripts/build_dfs_player_week_dataset.py first.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    df = pl.read_parquet(INPUT)

    required = {
        "position_group", "season", "week", "player_id", "split", "has_prior_game",
        TARGET, PREDICTION, "targets", "carries", "receptions",
    }
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError("Missing required fields: " + ", ".join(sorted(missing)))

    baseline = df.filter(
        pl.col("has_prior_game") & pl.col(PREDICTION).is_not_null() & pl.col(TARGET).is_not_null()
    )

    metrics = [metric_row(baseline, "ALL")]
    for position in POSITIONS:
        metrics.append(metric_row(baseline.filter(pl.col("position_group") == position), position))
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

    figures = [
        save_distribution_chart(df),
        save_mean_points_chart(position_summary),
        save_baseline_error_chart(metrics_df),
        save_actual_vs_prediction_chart(baseline),
        save_usage_chart(df),
    ]

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
        "figures": [str(path) for path in figures],
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
    print("Generated figures:")
    for path in figures:
        print(f"  {path}")
    print()
    print(f"Metrics CSV: {BASELINE_CSV}")
    print(f"Position summary CSV: {SUMMARY_CSV}")
    print(f"EDA JSON: {EDA_JSON}")


if __name__ == "__main__":
    main()
