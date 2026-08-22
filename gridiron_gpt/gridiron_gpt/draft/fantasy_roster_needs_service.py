from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RosterNeed:
    position: str
    current: int
    target: int

    @property
    def deficit(self) -> int:
        return max(0, self.target - self.current)

    @property
    def filled(self) -> bool:
        return self.deficit == 0


class FantasyRosterNeedsService:
    """Describe roster construction needs without changing player rankings.

    Targets are intentionally modest starter-oriented defaults. The service is
    advisory only: it reports positional deficits so draft-day presentation can
    add roster context while the production ranking_score remains untouched.
    """

    DEFAULT_TARGETS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1}

    def __init__(self, targets: dict[str, int] | None = None):
        configured = dict(targets or self.DEFAULT_TARGETS)
        if any(target < 0 for target in configured.values()):
            raise ValueError("roster targets cannot be negative")
        self.targets = {str(position).upper(): int(target) for position, target in configured.items()}

    def evaluate(self, roster_scores: Iterable[object]) -> dict[str, RosterNeed]:
        counts = {position: 0 for position in self.targets}
        for score in roster_scores:
            position = str(getattr(score, "position", "") or "").upper()
            if position in counts:
                counts[position] += 1

        return {
            position: RosterNeed(position=position, current=counts[position], target=target)
            for position, target in self.targets.items()
        }

    def needed_positions(self, roster_scores: Iterable[object]) -> tuple[str, ...]:
        needs = self.evaluate(roster_scores)
        return tuple(position for position, need in needs.items() if not need.filled)

    def need_for(self, position: str, roster_scores: Iterable[object]) -> RosterNeed | None:
        return self.evaluate(roster_scores).get(str(position or "").upper())
