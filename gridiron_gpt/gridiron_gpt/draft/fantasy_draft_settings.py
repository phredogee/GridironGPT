from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FantasyDraftSettings:
    """Validated league settings needed for snake-draft advisory services."""

    league_size: int = 12
    draft_slot: int = 1

    def __post_init__(self) -> None:
        if self.league_size < 2:
            raise ValueError("league_size must be at least 2")
        if self.draft_slot < 1 or self.draft_slot > self.league_size:
            raise ValueError("draft_slot must be between 1 and league_size")
