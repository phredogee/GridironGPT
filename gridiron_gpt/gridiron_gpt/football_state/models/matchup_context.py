from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MatchupTendency(str, Enum):
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OpponentMetric:
    name: str
    value: float
    league_average: float
    higher_is_favorable: bool = True
    sample_games: int = 0

    @property
    def relative_delta(self) -> float:
        if self.league_average == 0:
            return 0.0
        return (self.value - self.league_average) / abs(self.league_average)

    @property
    def favorable_delta(self) -> float:
        delta = self.relative_delta
        return delta if self.higher_is_favorable else -delta


@dataclass(frozen=True)
class MatchupContext:
    team: str
    opponent: str
    position: str
    season: int
    week: int
    tendency: MatchupTendency
    score: float
    confidence: float
    metrics: tuple[OpponentMetric, ...] = ()
    reason: str = ""
    source: str = "opponent matchup context"
    evidence: dict[str, Any] = field(default_factory=dict)
