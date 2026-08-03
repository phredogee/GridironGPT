from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DraftCapitalTier(str, Enum):
    PREMIUM = "premium"
    EARLY = "early"
    MIDDLE = "middle"
    LATE = "late"
    UNDRAFTED = "undrafted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CanonicalDraftContext:
    player_id: str
    player_name: str
    draft_year: int | None = None
    draft_round: int | None = None
    draft_pick: int | None = None
    college: str | None = None
    drafted_team: str | None = None
    source: str = "canonical draft context"
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.player_id.strip() or not self.player_name.strip():
            raise ValueError("player identity is required")
        if self.draft_round is not None and not 1 <= self.draft_round <= 7:
            raise ValueError("draft_round must be between 1 and 7")
        if self.draft_pick is not None and self.draft_pick <= 0:
            raise ValueError("draft_pick must be positive")

    def is_rookie(self, season: int) -> bool:
        return self.draft_year == season

    @property
    def capital_tier(self) -> DraftCapitalTier:
        if self.draft_year is None:
            return DraftCapitalTier.UNKNOWN
        if self.draft_round is None and self.draft_pick is None:
            return DraftCapitalTier.UNDRAFTED
        pick = self.draft_pick
        round_ = self.draft_round
        if (pick is not None and pick <= 32) or round_ == 1:
            return DraftCapitalTier.PREMIUM
        if (pick is not None and pick <= 96) or round_ in {2, 3}:
            return DraftCapitalTier.EARLY
        if (pick is not None and pick <= 160) or round_ in {4, 5}:
            return DraftCapitalTier.MIDDLE
        return DraftCapitalTier.LATE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CanonicalDraftContext":
        return cls(**payload)
