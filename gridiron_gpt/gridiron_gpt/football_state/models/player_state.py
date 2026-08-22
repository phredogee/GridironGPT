from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class CanonicalPlayerState:
    """Canonical snapshot of a player's current NFL football state."""

    player_id: str
    player_name: str
    team: str | None = None
    position: str | None = None
    roster_status: str | None = None
    status_description_abbr: str | None = None
    roster_week: int | None = None
    roster_game_type: str | None = None
    depth_chart_position: str | None = None
    jersey_number: int | str | None = None
    years_experience: int | float | None = None
    college: str | None = None
    rookie_year: int | None = None
    entry_year: int | None = None
    draft_club: str | None = None
    draft_number: int | None = None
    identifiers: dict[str, str] = field(default_factory=dict)
    effective_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "nflverse roster"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["effective_at"] = self.effective_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalPlayerState":
        values = dict(payload)
        effective_at = values.get("effective_at")
        if isinstance(effective_at, str):
            values["effective_at"] = datetime.fromisoformat(effective_at)
        return cls(**values)
