from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AvailabilityDesignation(str, Enum):
    ACTIVE = "active"
    QUESTIONABLE = "questionable"
    DOUBTFUL = "doubtful"
    OUT = "out"
    IR = "ir"
    PUP = "pup"
    NFI = "nfi"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class PracticeParticipation(str, Enum):
    FULL = "full"
    LIMITED = "limited"
    DNP = "dnp"
    NOT_REPORTED = "not_reported"


@dataclass(frozen=True)
class CanonicalAvailabilityState:
    """Canonical snapshot of a player's current availability and practice state."""

    player_id: str
    player_name: str
    team: str | None = None
    designation: AvailabilityDesignation = AvailabilityDesignation.UNKNOWN
    practice_participation: PracticeParticipation = PracticeParticipation.NOT_REPORTED
    injury: str | None = None
    effective_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "canonical football state"
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def available(self) -> bool | None:
        if self.designation == AvailabilityDesignation.ACTIVE:
            return True
        if self.designation in {
            AvailabilityDesignation.OUT,
            AvailabilityDesignation.IR,
            AvailabilityDesignation.PUP,
            AvailabilityDesignation.NFI,
            AvailabilityDesignation.SUSPENDED,
        }:
            return False
        return None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["designation"] = self.designation.value
        payload["practice_participation"] = self.practice_participation.value
        payload["effective_at"] = self.effective_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalAvailabilityState":
        values = dict(payload)
        values["designation"] = AvailabilityDesignation(values.get("designation", "unknown"))
        values["practice_participation"] = PracticeParticipation(
            values.get("practice_participation", "not_reported")
        )
        effective_at = values.get("effective_at")
        if isinstance(effective_at, str):
            values["effective_at"] = datetime.fromisoformat(effective_at)
        return cls(**values)
