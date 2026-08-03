from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from gridiron_gpt.football_state.models.game_context import (
    CanonicalGameContext,
    VenueSide,
)


@dataclass(frozen=True)
class UpcomingScheduleContext:
    team: str
    season: int
    as_of_week: int
    next_game: CanonicalGameContext | None
    opponent: str | None
    venue_side: VenueSide | None
    bye_week: bool
    days_rest: float | None
    previous_game_id: str | None = None

    @property
    def has_upcoming_game(self) -> bool:
        return self.next_game is not None

    @property
    def short_rest(self) -> bool:
        return self.days_rest is not None and self.days_rest < 6.0

    @property
    def extended_rest(self) -> bool:
        return self.days_rest is not None and self.days_rest > 8.0
