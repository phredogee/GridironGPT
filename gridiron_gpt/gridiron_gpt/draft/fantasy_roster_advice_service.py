from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_gpt.draft.fantasy_roster_needs_service import FantasyRosterNeedsService, RosterNeed


@dataclass(frozen=True)
class RosterAdvice:
    needs: Mapping[str, RosterNeed]

    @property
    def active_needs(self) -> tuple[RosterNeed, ...]:
        return tuple(need for need in self.needs.values() if not need.filled)

    @property
    def summary(self) -> str:
        active = self.active_needs
        if not active:
            return "Starter needs filled"
        return "Roster Needs: " + " · ".join(f"{need.position} ({need.deficit})" for need in active)

    def badge_for(self, position: str | None) -> str:
        need = self.needs.get(str(position or "").upper())
        if need is None or need.filled:
            return ""
        return f"Fills {need.position} need"


class FantasyRosterAdviceService:
    """Build advisory draft context without re-ranking players."""

    def __init__(self, needs_service: FantasyRosterNeedsService | None = None):
        self.needs_service = needs_service or FantasyRosterNeedsService()

    def build(self, roster_scores: Iterable[object]) -> RosterAdvice:
        return RosterAdvice(needs=self.needs_service.evaluate(roster_scores))
