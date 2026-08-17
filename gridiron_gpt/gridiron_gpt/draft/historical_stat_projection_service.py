from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from gridiron_gpt.draft.fantasy_projection_service import PlayerStatProjection
from gridiron_gpt.draft.scorer import SEASONS, SEASON_WEIGHTS


class HistoricalStatProjectionService:
    """Build a conservative next-season stat line from recent NFL production."""

    STAT_COLUMNS = (
        "passing_yards", "passing_tds", "interceptions", "rushing_yards",
        "rushing_tds", "receptions", "receiving_yards", "receiving_tds",
        "rushing_fumbles_lost", "receiving_fumbles_lost",
        "passing_2pt_conversions", "rushing_2pt_conversions",
        "receiving_2pt_conversions",
    )
    FULL_CONFIDENCE_GAMES = 17.0

    def __init__(self, *, stats_loader: Callable | None = None) -> None:
        self.stats_loader = stats_loader or self._load_nfl_stats

    def build(self, *, seasons: list[int] | None = None, expected_games: float = 17.0) -> dict[str, PlayerStatProjection]:
        seasons = seasons or list(SEASONS)
        if expected_games < 0:
            raise ValueError("expected_games cannot be negative")
        frames = []
        for season in seasons:
            frame = self.stats_loader(season=season)
            if frame is None or frame.empty:
                continue
            frame = self._season_totals(frame.copy(), season=season)
            if not frame.empty:
                frames.append(frame)
        if not frames:
            return {}
        combined = pd.concat(frames, ignore_index=True)
        projections = {}
        for player_name, rows in combined.groupby("player_display_name"):
            projection = self._blend_player(rows, expected_games=expected_games)
            if projection is not None:
                projections[str(player_name)] = projection
        return projections

    def _season_totals(self, frame: pd.DataFrame, *, season: int) -> pd.DataFrame:
        if "player_display_name" not in frame.columns:
            return pd.DataFrame()
        if "season_type" in frame.columns:
            frame = frame[frame["season_type"].astype(str).str.upper().eq("REG")]
        if frame.empty:
            return frame
        if "games" in frame.columns or "games_played" in frame.columns:
            frame["season"] = season
            return frame
        numeric = [column for column in self.STAT_COLUMNS if column in frame.columns]
        grouped = frame.groupby("player_display_name", as_index=False)[numeric].sum() if numeric else frame[["player_display_name"]].drop_duplicates()
        games = (frame.groupby("player_display_name")["week"].nunique().rename("games") if "week" in frame.columns else frame.groupby("player_display_name").size().rename("games"))
        grouped = grouped.merge(games, on="player_display_name", how="left")
        grouped["season"] = season
        return grouped

    def _blend_player(self, rows: pd.DataFrame, *, expected_games: float) -> PlayerStatProjection | None:
        weighted = {column: 0.0 for column in self.STAT_COLUMNS}
        total_weight = 0.0
        weighted_games = 0.0
        for _, row in rows.iterrows():
            season = int(row["season"])
            weight = float(SEASON_WEIGHTS.get(season, 0.0))
            games = self._games(row)
            if weight <= 0 or games <= 0:
                continue
            total_weight += weight
            weighted_games += games * weight
            for column in self.STAT_COLUMNS:
                weighted[column] += (self._number(row.get(column, 0.0)) / games) * weight
        if total_weight <= 0:
            return None
        observed_games = weighted_games / total_weight
        confidence = min(1.0, observed_games / self.FULL_CONFIDENCE_GAMES)
        annual = {key: (value / total_weight) * expected_games * confidence for key, value in weighted.items()}
        return PlayerStatProjection(
            games=expected_games,
            passing_yards=annual["passing_yards"], passing_touchdowns=annual["passing_tds"],
            interceptions=annual["interceptions"], rushing_yards=annual["rushing_yards"],
            rushing_touchdowns=annual["rushing_tds"], receptions=annual["receptions"],
            receiving_yards=annual["receiving_yards"], receiving_touchdowns=annual["receiving_tds"],
            fumbles_lost=annual["rushing_fumbles_lost"] + annual["receiving_fumbles_lost"],
            two_point_conversions=annual["passing_2pt_conversions"] + annual["rushing_2pt_conversions"] + annual["receiving_2pt_conversions"],
        )

    @staticmethod
    def _games(row: pd.Series) -> float:
        for column in ("games", "games_played"):
            value = HistoricalStatProjectionService._number(row.get(column))
            if value > 0:
                return value
        return 0.0

    @staticmethod
    def _number(value) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        return value if pd.notna(value) else 0.0

    @staticmethod
    def _load_nfl_stats(*, season: int) -> pd.DataFrame:
        import nflreadpy as nfl
        frame = nfl.load_player_stats(seasons=[season])
        if hasattr(frame, "to_pandas"):
            frame = frame.to_pandas()
        return frame
