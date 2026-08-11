from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class CanonicalGameState:
    """Canonical snapshot of an NFL game's schedule/state context."""

    game_id: str
    season: int
    week: int
    season_type: str
    home_team: str
    away_team: str
    kickoff_at: datetime | None = None
    game_status: str | None = None
    venue: str | None = None
    effective_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "nflverse schedule"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kickoff_at"] = self.kickoff_at.isoformat() if self.kickoff_at else None
        payload["effective_at"] = self.effective_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalGameState":
        values = dict(payload)
        for field_name in ("kickoff_at", "effective_at"):
            value = values.get(field_name)
            if isinstance(value, str):
                values[field_name] = datetime.fromisoformat(value)
        return cls(**values)
