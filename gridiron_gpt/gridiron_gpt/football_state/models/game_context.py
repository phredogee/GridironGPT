from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELED = "canceled"


class VenueSide(str, Enum):
    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class CanonicalGameContext:
    """Stable schedule facts for one NFL game."""

    game_id: str
    season: int
    week: int
    season_type: str
    home_team: str
    away_team: str
    kickoff_at: datetime
    status: GameStatus = GameStatus.SCHEDULED
    neutral_site: bool = False
    source: str = "canonical game context"
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.game_id.strip():
            raise ValueError("game_id is required")
        if self.season <= 0:
            raise ValueError("season must be positive")
        if self.week <= 0:
            raise ValueError("week must be positive")
        if not self.season_type.strip():
            raise ValueError("season_type is required")
        if not self.home_team.strip() or not self.away_team.strip():
            raise ValueError("home_team and away_team are required")
        if self.home_team == self.away_team:
            raise ValueError("home_team and away_team must differ")
        if self.kickoff_at.tzinfo is None:
            raise ValueError("kickoff_at must be timezone-aware")

    @property
    def completed(self) -> bool:
        return self.status == GameStatus.FINAL

    def includes_team(self, team: str) -> bool:
        return team in {self.home_team, self.away_team}

    def opponent_for(self, team: str) -> str:
        if team == self.home_team:
            return self.away_team
        if team == self.away_team:
            return self.home_team
        raise ValueError(f"team {team!r} is not part of game {self.game_id}")

    def venue_side_for(self, team: str) -> VenueSide:
        if not self.includes_team(team):
            raise ValueError(f"team {team!r} is not part of game {self.game_id}")
        if self.neutral_site:
            return VenueSide.NEUTRAL
        return VenueSide.HOME if team == self.home_team else VenueSide.AWAY

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kickoff_at"] = self.kickoff_at.isoformat()
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalGameContext":
        values = dict(payload)
        kickoff_at = values.get("kickoff_at")
        if isinstance(kickoff_at, str):
            values["kickoff_at"] = datetime.fromisoformat(kickoff_at)
        status = values.get("status")
        if isinstance(status, str):
            values["status"] = GameStatus(status)
        return cls(**values)
