from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScoringFormat(str, Enum):
    STANDARD = "standard"
    HALF_PPR = "half_ppr"
    PPR = "ppr"


class DecisionType(str, Enum):
    DRAFT = "draft"
    START_SIT = "start_sit"
    WAIVER = "waiver"
    TRADE = "trade"
    ROSTER = "roster"


class RecommendationAction(str, Enum):
    TARGET = "target"
    DRAFT = "draft"
    START = "start"
    SIT = "sit"
    ADD = "add"
    PASS = "pass"
    ACCEPT = "accept"
    REJECT = "reject"
    HOLD = "hold"


@dataclass(frozen=True)
class LeagueContext:
    scoring_format: ScoringFormat = ScoringFormat.HALF_PPR
    teams: int = 12
    roster_size: int = 16
    starting_slots: dict[str, int] = field(
        default_factory=lambda: {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}
    )
    faab_budget: int = 100

    def __post_init__(self) -> None:
        if self.teams <= 1:
            raise ValueError("teams must be greater than one")
        if self.roster_size <= 0:
            raise ValueError("roster_size must be positive")
        if self.faab_budget < 0:
            raise ValueError("faab_budget must be non-negative")


@dataclass(frozen=True)
class PlayerDecisionInput:
    player_id: str
    player_name: str
    position: str
    team: str | None
    cortex_score: float
    confidence: float
    projected_points: float = 0.0
    replacement_value: float = 0.0
    availability_factor: float = 1.0
    matchup_factor: float = 0.0
    trend_factor: float = 0.0
    rostered: bool = False
    bye_week: bool = False
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.player_id.strip() or not self.player_name.strip():
            raise ValueError("player identity is required")
        if not self.position.strip():
            raise ValueError("position is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not 0.0 <= self.availability_factor <= 1.0:
            raise ValueError("availability_factor must be between 0 and 1")


@dataclass(frozen=True)
class FantasyDecision:
    decision_type: DecisionType
    action: RecommendationAction
    player_id: str | None
    player_name: str | None
    score: float
    confidence: float
    summary: str
    reasons: tuple[str, ...]
    alternatives: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TradeSide:
    players: tuple[PlayerDecisionInput, ...]

    @property
    def value(self) -> float:
        return sum(
            player.cortex_score
            + player.projected_points
            + player.replacement_value
            for player in self.players
        )
