"""Build the Phase 2 regular-season NFL player-week dataset.

This script loads nflverse player statistics through nflreadpy, filters to
regular-season observations, writes an immutable raw snapshot, creates a
smaller canonical player-week table, assigns chronological split labels, and
writes a JSON quality report.

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


def build_quality_report(
    frame: pl.DataFrame,
    start_season: int,
    end_season: int,
) -> dict:
    duplicate_rows = (
        frame.group_by(["season", "week", "game_id", "player_id"])
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    season_counts = {
        str(row["season"]): row["len"]
        for row in frame.group_by("season").len().sort("season").to_dicts()
    }

    week_ranges = {
        str(row["season"]): {
            "min_week": row["min_week"],
            "max_week": row["max_week"],
        }
        for row in (
            frame.group_by("season")
            .agg(
                pl.col("week").min().alias("min_week"),
                pl.col("week").max().alias("max_week"),
            )
            .sort("season")
            .to_dicts()
        )
    }

    return {
        "source": "nflverse via nflreadpy",
        "season_type": "REG",
        "start_season": start_season,
        "end_season": end_season,
        "rows": frame.height,
        "columns": len(frame.columns),
        "season_counts": season_counts,
        "week_ranges": week_ranges,
        "duplicate_player_game_keys": duplicate_rows,
        "missing_player_id": frame["player_id"].null_count(),
        "missing_game_id": frame["game_id"].null_count(),
        "missing_position": frame["position"].null_count()
        if "position" in frame.columns
        else None,
        "missing_fantasy_points": frame["fantasy_points"].null_count()
        if "fantasy_points" in frame.columns
        else None,
        "missing_fantasy_points_ppr": frame["fantasy_points_ppr"].null_count()
        if "fantasy_points_ppr" in frame.columns
        else None,
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
    reports_dir = args.output_root / "reports"

    for directory in (raw_dir, interim_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    frame = load_regular_season_stats(args.start_season, args.end_season)

    missing_core = [column for column in CORE_COLUMNS if column not in frame.columns]
    if missing_core:
        raise RuntimeError(
            "Expected core columns are missing from nflverse: "
            + ", ".join(missing_core)
        )

    span = f"{args.start_season}_{args.end_season}"

    raw_path = raw_dir / f"nflverse_player_week_{span}_reg.parquet"
    canonical_path = interim_dir / f"player_week_core_{span}_reg.parquet"
    report_path = reports_dir / f"player_week_quality_{span}.json"

    # Preserve every source field in the raw regular-season snapshot.
    frame.write_parquet(raw_path)

    # Canonical Phase 2 table: selected source fields + chronological split.
    canonical = frame.select(CORE_COLUMNS).with_columns(split_expr())
    canonical.write_parquet(canonical_path)

    report = build_quality_report(frame, args.start_season, args.end_season)
    report["raw_path"] = str(raw_path)
    report["canonical_path"] = str(canonical_path)
    report["canonical_columns"] = canonical.columns

    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("DFS Phase 2 player-week build complete")
    print(f"Regular-season rows: {frame.height:,}")
    print(f"Source columns: {len(frame.columns)}")
    print(f"Canonical columns: {len(canonical.columns)}")
    print(f"Raw snapshot: {raw_path}")
    print(f"Canonical table: {canonical_path}")
    print(f"Quality report: {report_path}")
    print()
    print("Season counts:")
    for season, count in report["season_counts"].items():
        print(f"  {season}: {count:,}")
    print()
    print(
        "Duplicate player-game keys:",
        report["duplicate_player_game_keys"],
    )


if __name__ == "__main__":
    main()
