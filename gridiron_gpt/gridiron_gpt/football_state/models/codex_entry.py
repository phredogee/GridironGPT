from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CodexEntryType(str, Enum):
    TEAM_HISTORY = "team_history"
    ROLE_HISTORY = "role_history"
    AVAILABILITY_HISTORY = "availability_history"
    PRODUCTION_HISTORY = "production_history"
    RELATIONSHIP_HISTORY = "relationship_history"
    CAREER_MILESTONE = "career_milestone"


@dataclass(frozen=True)
class CodexEntry:
    player_id: str
    player_name: str
    entry_type: CodexEntryType
    season: int
    summary: str
    occurred_at: datetime
    team: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    source: str = "gridiron codex"
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.player_id.strip() or not self.player_name.strip():
            raise ValueError("player identity is required")
        if not self.summary.strip():
            raise ValueError("summary is required")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")

    def fingerprint(self) -> str:
        return ":".join([
            self.player_id,
            self.entry_type.value,
            str(self.season),
            self.occurred_at.isoformat(),
            self.summary.strip().lower(),
        ])

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["entry_type"] = self.entry_type.value
        payload["occurred_at"] = self.occurred_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CodexEntry":
        values = dict(payload)
        values["entry_type"] = CodexEntryType(values["entry_type"])
        values["occurred_at"] = datetime.fromisoformat(values["occurred_at"])
        return cls(**values)
