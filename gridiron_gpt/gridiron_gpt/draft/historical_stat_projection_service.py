from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from gridiron_gpt.draft.fantasy_projection_service import PlayerStatProjection
from gridiron_gpt.draft.scorer import SEASONS, SEASON_WEIGHTS


class HistoricalStatProjectionService:
    """Build a conservative next-season stat line from recent NFL production.

    Each season is first converted to per-game production, then blended using
    the same 15/30/55 recency weights already used by the rankings baseline.
    V1 annualizes that blend to the requested expected-games value. It does not
    use ADP or the GridironGPT composite score.
    """

    STAT_COLUMNS = (
        "passing_yards",
        "passing_tds",
        "interceptions",
        "rushing_yards",
        "rushing_tds",
        "receptions",
        "receiving_yards",
        "receiving_tds",
        "rushing_fumbles_lost",
        "receiving_fumbles_lost",
        "passing_2pt_conversions",
        "rushing_2pt_conversions",
        "receiving_2pt_conversions",
    )

    def __init__(self, *, stats_loader: Callable | None = None) -> None:
        self.stats_loader = stats_loader or self._load_nfl_stats

    def build(
        self,
        *,
        seasons: list[int] | None = None,
        expected_games: float = 17.0,
    ) -> dict[str, PlayerStatProjection]:
        seasons = seasons or list(SEASONS)
        if expected_games < 0:
            raise ValueError("expected_games cannot be negative")

        frames: list[pd.DataFrame] = []
        for season in seasons:
            frame = self.stats_loader(season=season)
            if frame is None or frame.empty:
                continue
            frame = frame.copy()
            frame["season"] = season
            frames.append(frame)

        if not frames:
            return {}

        combined = pd.concat(frames, ignore_index=True)
        projections: dict[str, PlayerStatProjection] = {}
        for player_name, player_rows in combined.groupby("player_display_name"):
            blended = self._blend_player(player_rows, expected_games=expected_games)
            if blended is not None:
                projections[str(player_name)] = blended
        return projections

    def _blend_player(
        self, rows: pd.DataFrame, *, expected_games: float
    ) -> PlayerStatProjection | None:
        weighted: dict[str, float] = {column: 0.0 for column in self.STAT_COLUMNS}
        total_weight = 0.0

        for _, row in rows.iterrows():
            season = int(row["season"])
            weight = float(SEASON_WEIGHTS.get(season, 0.0))
            games = self._games(row)
            if weight <= 0 or games <= 0:
                continue
            total_weight += weight
            for column in self.STAT_COLUMNS:
                value = self._number(row.get(column, 0.0))
                weighted[column] += (value / games) * weight

        if total_weight <= 0:
            return None

        annual = {
            key: (value / total_weight) * expected_games
            for key, value in weighted.items()
        }
        return PlayerStatProjection(
            games=expected_games,
            passing_yards=annual["passing_yards"],
            passing_touchdowns=annual["passing_tds"],
            interceptions=annual["interceptions"],
            rushing_yards=annual["rushing_yards"],
            rushing_touchdowns=annual["rushing_tds"],
            receptions=annual["receptions"],
            receiving_yards=annual["receiving_yards"],
            receiving_touchdowns=annual["receiving_tds"],
            fumbles_lost=(
                annual["rushing_fumbles_lost"]
                + annual["receiving_fumbles_lost"]
            ),
            two_point_conversions=(
                annual["passing_2pt_conversions"]
                + annual["rushing_2pt_conversions"]
                + annual["receiving_2pt_conversions"]
            ),
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
