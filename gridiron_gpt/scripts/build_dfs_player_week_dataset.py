"""Build the Phase 2 regular-season NFL player-week dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import nflreadpy as nfl
import polars as pl

DEFAULT_START_SEASON = 2020
DEFAULT_END_SEASON = 2025
DFS_OFFENSIVE_GROUPS = ["QB", "RB", "WR", "TE"]

CORE_COLUMNS = [
    "player_id", "player_name", "player_display_name", "position", "position_group",
    "season", "week", "season_type", "game_id", "team", "opponent_team",
    "completions", "attempts", "passing_yards", "passing_tds",
    "passing_interceptions", "passing_air_yards", "passing_epa", "passing_cpoe",
    "carries", "rushing_yards", "rushing_tds", "rushing_epa", "receptions",
    "targets", "receiving_yards", "receiving_tds", "receiving_air_yards",
    "receiving_yards_after_catch", "receiving_epa", "target_share",
    "air_yards_share", "wopr", "special_teams_tds", "fantasy_points",
    "fantasy_points_ppr",
]

ROLLING_SOURCE_COLUMNS = [
    "fantasy_points", "fantasy_points_ppr", "targets", "carries", "receptions",
    "passing_yards", "rushing_yards", "receiving_yards", "target_share",
    "air_yards_share", "wopr",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the DFS Capstone player-week dataset.")
    parser.add_argument("--start-season", type=int, default=DEFAULT_START_SEASON)
    parser.add_argument("--end-season", type=int, default=DEFAULT_END_SEASON)
    parser.add_argument("--output-root", type=Path, default=Path("data/dfs"))
    return parser.parse_args()


def split_expr() -> pl.Expr:
    return (
        pl.when(pl.col("season") <= 2023).then(pl.lit("train"))
        .when(pl.col("season") == 2024).then(pl.lit("validation"))
        .when(pl.col("season") == 2025).then(pl.lit("test"))
        .otherwise(pl.lit("unassigned")).alias("split")
    )


def load_regular_season_stats(start_season: int, end_season: int) -> pl.DataFrame:
    frame = nfl.load_player_stats(list(range(start_season, end_season + 1)))
    required = {"season", "week", "season_type", "player_id", "game_id"}
    missing = required.difference(frame.columns)
    if missing:
        raise RuntimeError("Missing required nflverse fields: " + ", ".join(sorted(missing)))
    return frame.filter(pl.col("season_type") == "REG").sort(
        ["season", "week", "game_id", "player_id"]
    )


def clean_canonical_rows(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.filter(
        pl.col("player_id").is_not_null()
        & pl.col("position").is_not_null()
        & pl.col("player_name").is_not_null()
    )


def add_leakage_safe_features(frame: pl.DataFrame) -> pl.DataFrame:
    group_keys = ["player_id", "season"]
    ordered = frame.sort(["player_id", "season", "week", "game_id"])
    expressions: list[pl.Expr] = []
    for column in ROLLING_SOURCE_COLUMNS:
        expressions.extend([
            pl.col(column).shift(1).over(group_keys).alias(f"{column}_lag1"),
            pl.col(column).shift(1).rolling_mean(window_size=3, min_samples=1)
            .over(group_keys).alias(f"{column}_roll3"),
            pl.col(column).shift(1).rolling_mean(window_size=5, min_samples=1)
            .over(group_keys).alias(f"{column}_roll5"),
        ])
    return ordered.with_columns(expressions).with_columns(
        pl.col("fantasy_points_lag1").is_not_null().alias("has_prior_game")
    )


def build_offensive_modeling_table(features: pl.DataFrame) -> pl.DataFrame:
    """Create the initial individual-player DFS population.

    Keep QB/RB/WR/TE position groups and retain cold-start rows. The
    has_prior_game flag allows baseline/model evaluation to treat those rows
    explicitly rather than silently deleting them. DST is modeled separately.
    """
    return (
        features.filter(pl.col("position_group").is_in(DFS_OFFENSIVE_GROUPS))
        .sort(["season", "week", "game_id", "player_id"])
    )


def counts_by_position(frame: pl.DataFrame) -> dict[str, int]:
    return {
        str(row["position_group"]): row["len"]
        for row in frame.group_by("position_group").len().sort("position_group").to_dicts()
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
    missing_core = [c for c in CORE_COLUMNS if c not in raw_frame.columns]
    if missing_core:
        raise RuntimeError("Expected core columns are missing: " + ", ".join(missing_core))

    span = f"{args.start_season}_{args.end_season}"
    raw_path = raw_dir / f"nflverse_player_week_{span}_reg.parquet"
    canonical_path = interim_dir / f"player_week_core_{span}_reg.parquet"
    features_path = processed_dir / f"player_week_features_{span}_reg.parquet"
    offense_path = processed_dir / f"dfs_offense_player_week_{span}_reg.parquet"
    report_path = reports_dir / f"player_week_quality_{span}.json"

    raw_frame.write_parquet(raw_path)
    canonical = (
        clean_canonical_rows(raw_frame.select(CORE_COLUMNS))
        .with_columns(split_expr())
        .sort(["season", "week", "game_id", "player_id"])
    )
    canonical.write_parquet(canonical_path)

    features = add_leakage_safe_features(canonical)
    features.write_parquet(features_path)

    offense = build_offensive_modeling_table(features)
    offense.write_parquet(offense_path)

    duplicate_rows = (
        canonical.group_by(["season", "week", "game_id", "player_id"])
        .len().filter(pl.col("len") > 1).height
    )
    cold_start = offense.filter(~pl.col("has_prior_game"))
    baseline_ready = offense.filter(pl.col("has_prior_game"))

    report = {
        "source": "nflverse via nflreadpy",
        "season_type": "REG",
        "start_season": args.start_season,
        "end_season": args.end_season,
        "raw_regular_season_rows": raw_frame.height,
        "raw_columns": len(raw_frame.columns),
        "clean_canonical_rows": canonical.height,
        "rows_removed_missing_identity": raw_frame.height - canonical.height,
        "canonical_columns": len(canonical.columns),
        "feature_rows": features.height,
        "feature_columns": len(features.columns),
        "duplicate_player_game_keys": duplicate_rows,
        "raw_missing_player_id": raw_frame["player_id"].null_count(),
        "raw_missing_position": raw_frame["position"].null_count(),
        "raw_missing_game_id": raw_frame["game_id"].null_count(),
        "raw_missing_fantasy_points": raw_frame["fantasy_points"].null_count(),
        "raw_missing_fantasy_points_ppr": raw_frame["fantasy_points_ppr"].null_count(),
        "dfs_offensive_position_groups": DFS_OFFENSIVE_GROUPS,
        "dfs_offensive_rows": offense.height,
        "dfs_offensive_counts_by_position_group": counts_by_position(offense),
        "dfs_offensive_cold_start_rows": cold_start.height,
        "dfs_offensive_cold_start_by_position_group": counts_by_position(cold_start),
        "dfs_offensive_baseline_ready_rows": baseline_ready.height,
        "feature_policy": {
            "windows": [1, 3, 5],
            "grouping": ["player_id", "season"],
            "current_game_shifted_out": True,
            "bye_weeks_treated_as_zero": False,
            "cross_season_history_used": False,
            "cold_start_rows_retained": True,
            "dst_modeled_separately": True,
        },
        "split_policy": {
            "train": "2020-2023", "validation": "2024", "test": "2025", "live": "2026"
        },
        "raw_path": str(raw_path),
        "canonical_path": str(canonical_path),
        "features_path": str(features_path),
        "dfs_offense_path": str(offense_path),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("DFS Phase 2 player-week build complete")
    print(f"Raw regular-season rows: {raw_frame.height:,}")
    print(f"Clean canonical rows: {canonical.height:,}")
    print(f"Rows removed for missing player identity/position: {raw_frame.height - canonical.height:,}")
    print(f"Feature columns: {len(features.columns)}")
    print(f"DFS offensive rows (QB/RB/WR/TE): {offense.height:,}")
    print(f"Baseline-ready offensive rows: {baseline_ready.height:,}")
    print(f"Cold-start offensive rows retained: {cold_start.height:,}")
    print(f"DFS offense table: {offense_path}")
    print(f"Quality report: {report_path}")
    print("Position-group counts:")
    for position, count in counts_by_position(offense).items():
        print(f"  {position}: {count:,}")
    print("Cold-start counts:")
    for position, count in counts_by_position(cold_start).items():
        print(f"  {position}: {count:,}")
    print("Duplicate player-game keys:", duplicate_rows)


if __name__ == "__main__":
    main()
