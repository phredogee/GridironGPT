from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState


class UsageTrendDirection(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class UsageMetricDelta:
    metric: str
    baseline: float
    current: float
    delta: float


@dataclass(frozen=True)
class UsageTrendResult:
    player_id: str
    player_name: str
    direction: UsageTrendDirection
    current: CanonicalUsageState
    prior_games: int
    deltas: dict[str, UsageMetricDelta] = field(default_factory=dict)
    reason: str = ""
