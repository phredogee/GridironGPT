from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from gridiron_gpt.football_state.models.availability_state import CanonicalAvailabilityState


class AvailabilityTrajectory(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"
    RECOVERED = "recovered"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AvailabilityTrajectoryResult:
    player_id: str
    player_name: str
    trajectory: AvailabilityTrajectory
    previous: CanonicalAvailabilityState
    current: CanonicalAvailabilityState
    reason: str
