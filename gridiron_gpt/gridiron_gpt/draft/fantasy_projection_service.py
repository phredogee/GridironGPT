from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FantasyScoring(str, Enum):
    STANDARD = "standard"
    HALF_PPR = "half_ppr"
    PPR = "ppr"


@dataclass(frozen=True)
class PlayerStatProjection:
    """Projected season counting stats used to calculate fantasy production."""

    games: float = 17.0
    passing_yards: float = 0.0
    passing_touchdowns: float = 0.0
    interceptions: float = 0.0
    rushing_yards: float = 0.0
    rushing_touchdowns: float = 0.0
    receptions: float = 0.0
    receiving_yards: float = 0.0
    receiving_touchdowns: float = 0.0
    fumbles_lost: float = 0.0
    two_point_conversions: float = 0.0


@dataclass(frozen=True)
class FantasyPointProjection:
    projected_points: float
    projected_ppg: float | None
    games: float
    scoring: FantasyScoring


class FantasyProjectionService:
    """Convert independent statistical projections into fantasy points.

    V1 deliberately does not use ADP or the GridironGPT composite ranking score.
    This keeps projected production an independent signal that can be validated
    before it is allowed to influence ranking weights.
    """

    RECEPTION_POINTS = {
        FantasyScoring.STANDARD: 0.0,
        FantasyScoring.HALF_PPR: 0.5,
        FantasyScoring.PPR: 1.0,
    }

    def project(
        self,
        stats: PlayerStatProjection,
        *,
        scoring: FantasyScoring | str = FantasyScoring.PPR,
    ) -> FantasyPointProjection:
        scoring = FantasyScoring(scoring)
        self._validate(stats)

        points = (
            stats.passing_yards / 25.0
            + stats.passing_touchdowns * 4.0
            - stats.interceptions * 2.0
            + stats.rushing_yards / 10.0
            + stats.rushing_touchdowns * 6.0
            + stats.receptions * self.RECEPTION_POINTS[scoring]
            + stats.receiving_yards / 10.0
            + stats.receiving_touchdowns * 6.0
            - stats.fumbles_lost * 2.0
            + stats.two_point_conversions * 2.0
        )
        points = round(points, 2)
        ppg = round(points / stats.games, 2) if stats.games > 0 else None
        return FantasyPointProjection(
            projected_points=points,
            projected_ppg=ppg,
            games=stats.games,
            scoring=scoring,
        )

    @staticmethod
    def _validate(stats: PlayerStatProjection) -> None:
        for field_name, value in stats.__dict__.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")
