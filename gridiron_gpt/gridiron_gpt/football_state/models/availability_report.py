from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    PracticeParticipation,
)


@dataclass(frozen=True)
class AvailabilityReport:
    """One source observation about a player's availability."""

    player_id: str
    player_name: str
    source: str
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    team: str | None = None
    designation: AvailabilityDesignation | None = None
    practice_participation: PracticeParticipation | None = None
    injury: str | None = None
    official: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
