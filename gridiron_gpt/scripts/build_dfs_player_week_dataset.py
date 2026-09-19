"""Build the Phase 2 regular-season NFL player-week dataset.

This script loads nflverse player statistics through nflreadpy, filters to
regular-season observations, preserves an immutable raw snapshot, creates a
clean canonical player-week table, generates leakage-safe lag/rolling
features, assigns chronological split labels, and writes a JSON quality
report.

Run from the repository's gridiron_gpt directory:

    python scripts/build_dfs_player_week_dataset.py

Optional:

    python scripts/build_dfs_player_week_dataset.py --start-season 2020 --end-season 2025
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import nflreadpy as nfl
import polars as pl


DEFAULT_START_SEASON = 2020
DEFAULT_END_SEASON = 2025

CORE_COLUMNS = [
    "player_id",
    "player_name",
    "player_display_name",
    "position",
    "position_group",
    "season",
    "week",
    "season_type",
    "game_id",
    "team",
    "opponent_team",
    "completions",
    "attempts",
    "passing_yards",
    "passing_tds",
    "passing_interceptions",
    "passing_air_yards",
    "passing_epa",
    "passing_cpoe",
    "carries",
    "rushing_yards",
    "rushing_tds",
    "rushing_epa",
    "receptions",
    "targets",
    "receiving_yards",
    "receiving_tds",
    "receiving_air_yards",
    "receiving_yards_after_catch",
    "receiving_epa",
    "target_share",
    "air_yards_share",
    "wopr",
    "special_teams_tds",
    "fantasy_points",
    "fantasy_points_ppr",
]

ROLLING_SOURCE_COLUMNS = [
    "fantasy_points",
    "fantasy_points_ppr",
    "targets",
    "carries",
    "receptions",
    "passing_yards",
    "rushing_yards",
    "receiving_yards",
    "target_share",
    "air_yards_share",
    "wopr",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the DFS Capstone regular-season player-week dataset."
    )
    parser.add_argument(
        "--start-season",
        type=int,
        default=DEFAULT_START_SEASON,
        help=f"First season to load (default: {DEFAULT_START_SEASON}).",
    )
    parser.add_argument(
        "--end-season",
        type=int,
        default=DEFAULT_END_SEASON,
        help=f"Last season to load (default: {DEFAULT_END_SEASON}).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/dfs"),
        help="Root output directory (default: data/dfs).",
    )
    return parser.parse_args()


def split_expr() -> pl.Expr:
    """Return the initial chronological split assignment."""
    return (
        pl.when(pl.col("season") <= 2023)
        .then(pl.lit("train"))
        .when(pl.col("season") == 2024)
        .then(pl.lit("validation"))
        .when(pl.col("season") == 2025)
        .then(pl.lit("test"))
        .otherwise(pl.lit("unassigned"))
        .alias("split")
    )


def load_regular_season_stats(start_season: int, end_season: int) -> pl.DataFrame:
    seasons = list(range(start_season, end_season + 1))
    frame = nfl.load_player_stats(seasons)

    required = {"season", "week", "season_type", "player_id", "game_id"}
    missing = required.difference(frame.columns)
    if missing:
        raise RuntimeError(
            "nflverse player-stat schema is missing required fields: "
            + ", ".join(sorted(missing))
        )

    return (
        frame.filter(pl.col("season_type") == "REG")
        .sort(["season", "week", "game_id", "player_id"])
    )


def clean_canonical_rows(frame: pl.DataFrame) -> pl.DataFrame:
    """Remove rows that cannot represent an identifiable DFS player."""
    return frame.filter(
        pl.col("player_id").is_not_null()
        & pl.col("position").is_not_null()
        & pl.col("player_name").is_not_null()
    )


def add_leakage_safe_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add prior-game and rolling features using only earlier appearances.

    Rolling windows are grouped by player and season. Because the current row
    is shifted out before each rolling calculation, Week N never contributes
    to its own predictors. Grouping by season also prevents Week 1 from using
    the prior season automatically.

    Bye weeks are naturally skipped because rolling windows operate on prior
    player appearances rather than treating a missing week as a zero.
    """
    group_keys = ["player_id", "season"]

    ordered = frame.sort(["player_id", "season", "week", "game_id"])

    expressions: list[pl.Expr] = []

    for column in ROLLING_SOURCE_COLUMNS:
        expressions.append(
            pl.col(column)
            .shift(1)
            .over(group_keys)
            .alias(f"{column}_lag1")
        )
        expressions.append(
            pl.col(column)
            .shift(1)
            .rolling_mean(window_size=3, min_samples=1)
            .over(group_keys)
            .alias(f"{column}_roll3")
        )
        expressions.append(
            pl.col(column)
            .shift(1)
            .rolling_mean(window_size=5, min_samples=1)
            .over(group_keys)
            .alias(f"{column}_roll5")
        )

    return ordered.with_columns(expressions)


def build_quality_report(
    raw_frame: pl.DataFrame,
    canonical: pl.DataFrame,
    features: pl.DataFrame,
    start_season: int,
    end_season: int,
) -> dict:
    duplicate_rows = (
        canonical.group_by(["season", "week", "game_id", "player_id"])
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    season_counts_raw = {
        str(row["season"]): row["len"]
        for row in raw_frame.group_by("season").len().sort("season").to_dicts()
    }

    season_counts_clean = {
        str(row["season"]): row["len"]
        for row in canonical.group_by("season").len().sort("season").to_dicts()
    }

    week_ranges = {
        str(row["season"]): {
            "min_week": row["min_week"],
            "max_week": row["max_week"],
        }
        for row in (
            canonical.group_by("season")
            .agg(
                pl.col("week").min().alias("min_week"),
                pl.col("week").max().alias("max_week"),
            )
            .sort("season")
            .to_dicts()
        )
    }

    first_game_feature_nulls = features["fantasy_points_lag1"].null_count()

    return {
        "source": "nflverse via nflreadpy",
        "season_type": "REG",
        "start_season": start_season,
        "end_season": end_season,
        "raw_regular_season_rows": raw_frame.height,
        "raw_columns": len(raw_frame.columns),
        "clean_canonical_rows": canonical.height,
        "rows_removed_missing_identity": raw_frame.height - canonical.height,
        "canonical_columns": len(canonical.columns),
        "feature_rows": features.height,
        "feature_columns": len(features.columns),
        "season_counts_raw": season_counts_raw,
        "season_counts_clean": season_counts_clean,
        "week_ranges": week_ranges,
        "duplicate_player_game_keys": duplicate_rows,
        "raw_missing_player_id": raw_frame["player_id"].null_count(),
        "raw_missing_game_id": raw_frame["game_id"].null_count(),
        "raw_missing_position": raw_frame["position"].null_count(),
        "raw_missing_fantasy_points": raw_frame["fantasy_points"].null_count(),
        "raw_missing_fantasy_points_ppr": raw_frame[
            "fantasy_points_ppr"
        ].null_count(),
        "feature_rows_without_prior_game": first_game_feature_nulls,
        "feature_policy": {
            "windows": [1, 3, 5],
            "grouping": ["player_id", "season"],
            "current_game_shifted_out": True,
            "bye_weeks_treated_as_zero": False,
            "cross_season_history_used": False,
        },
        "split_policy": {
            "train": "2020-2023",
            "validation": "2024",
            "test": "2025",
            "live": "2026",
        },
    }


def main() -> None:
    args = parse_args()

    if args.start_season > args.end_season:
        raise SystemExit("--start-season must be <= --end-season")

    raw_dir = args.output_root / "raw"
    interim_dir = args.output_root / "interim"
    processed_dir = args.output_root / "processed"
    reports_dir = args.output_root / "reports"

    for directory in (raw_dir, interim_dir, processed_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    raw_frame = load_regular_season_stats(args.start_season, args.end_season)

    missing_core = [
        column for column in CORE_COLUMNS if column not in raw_frame.columns
    ]
    if missing_core:
        raise RuntimeError(
            "Expected core columns are missing from nflverse: "
            + ", ".join(missing_core)
        )

    span = f"{args.start_season}_{args.end_season}"

    raw_path = raw_dir / f"nflverse_player_week_{span}_reg.parquet"
    canonical_path = interim_dir / f"player_week_core_{span}_reg.parquet"
    features_path = (
        processed_dir / f"player_week_features_{span}_reg.parquet"
    )
    report_path = reports_dir / f"player_week_quality_{span}.json"

    # Preserve every source field before player-level cleaning.
    raw_frame.write_parquet(raw_path)

    # Canonical player-level table: selected source fields, valid identities,
    # and chronological split assignment.
    canonical = (
        clean_canonical_rows(raw_frame.select(CORE_COLUMNS))
        .with_columns(split_expr())
        .sort(["season", "week", "game_id", "player_id"])
    )
    canonical.write_parquet(canonical_path)

    # ML-preprocessing table with leakage-safe prior-game/rolling features.
    features = add_leakage_safe_features(canonical)
    features.write_parquet(features_path)

    report = build_quality_report(
        raw_frame,
        canonical,
        features,
        args.start_season,
        args.end_season,
    )
    report["raw_path"] = str(raw_path)
    report["canonical_path"] = str(canonical_path)
    report["features_path"] = str(features_path)
    report["canonical_column_names"] = canonical.columns
    report["feature_column_names"] = features.columns

    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("DFS Phase 2 player-week build complete")
    print(f"Raw regular-season rows: {raw_frame.height:,}")
    print(f"Clean canonical rows: {canonical.height:,}")
    print(
        "Rows removed for missing player identity/position:",
        f"{raw_frame.height - canonical.height:,}",
    )
    print(f"Source columns: {len(raw_frame.columns)}")
    print(f"Canonical columns: {len(canonical.columns)}")
    print(f"Feature columns: {len(features.columns)}")
    print(f"Raw snapshot: {raw_path}")
    print(f"Canonical table: {canonical_path}")
    print(f"Feature table: {features_path}")
    print(f"Quality report: {report_path}")
    print()
    print("Clean season counts:")
    for season, count in report["season_counts_clean"].items():
        print(f"  {season}: {count:,}")
    print()
    print(
        "Duplicate player-game keys:",
        report["duplicate_player_game_keys"],
    )
    print(
        "Rows without a prior-game fantasy feature:",
        report["feature_rows_without_prior_game"],
    )


if __name__ == "__main__":
    main()
