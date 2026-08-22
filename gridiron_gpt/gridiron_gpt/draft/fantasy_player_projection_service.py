from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.draft.fantasy_projection_service import (
    FantasyPointProjection,
    FantasyProjectionService,
    FantasyScoring,
    PlayerStatProjection,
)
from gridiron_gpt.draft.historical_stat_projection_service import (
    HistoricalStatProjectionService,
)


@dataclass(frozen=True)
class PlayerFantasyProjection:
    """Complete player projection containing both stats and fantasy output."""

    player_name: str
    stats: PlayerStatProjection
    fantasy: FantasyPointProjection


class FantasyPlayerProjectionService:
    """Connect historical stat projection to fantasy point calculation."""

    def __init__(
        self,
        *,
        stat_projection_service: HistoricalStatProjectionService | None = None,
        fantasy_projection_service: FantasyProjectionService | None = None,
    ) -> None:
        self.stat_projection_service = (
            stat_projection_service or HistoricalStatProjectionService()
        )
        self.fantasy_projection_service = (
            fantasy_projection_service or FantasyProjectionService()
        )

    def build(
        self,
        *,
        scoring: FantasyScoring | str = FantasyScoring.PPR,
        seasons: list[int] | None = None,
        expected_games: float = 17.0,
    ) -> dict[str, PlayerFantasyProjection]:
        """Return projected stats and fantasy output keyed by player name."""
        stat_projections = self.stat_projection_service.build(
            seasons=seasons,
            expected_games=expected_games,
        )

        projections: dict[str, PlayerFantasyProjection] = {}
        for player_name, stats in stat_projections.items():
            fantasy = self.fantasy_projection_service.project(
                stats,
                scoring=scoring,
            )
            projections[player_name] = PlayerFantasyProjection(
                player_name=player_name,
                stats=stats,
                fantasy=fantasy,
            )
        return projections

    def ranked(
        self,
        *,
        scoring: FantasyScoring | str = FantasyScoring.PPR,
        seasons: list[int] | None = None,
        expected_games: float = 17.0,
    ) -> list[PlayerFantasyProjection]:
        """Return projections ordered by projected season fantasy points."""
        projections = self.build(
            scoring=scoring,
            seasons=seasons,
            expected_games=expected_games,
        )
        return sorted(
            projections.values(),
            key=lambda projection: (
                -projection.fantasy.projected_points,
                projection.player_name.casefold(),
            ),
        )
