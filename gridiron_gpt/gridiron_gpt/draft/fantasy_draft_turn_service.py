from __future__ import annotations


class FantasyDraftTurnService:
    """Deterministic snake-draft turn math for a user's draft slot."""

    def __init__(self, *, league_size: int, draft_slot: int) -> None:
        league_size = int(league_size)
        draft_slot = int(draft_slot)
        if league_size < 2:
            raise ValueError("league_size must be at least 2")
        if draft_slot < 1 or draft_slot > league_size:
            raise ValueError("draft_slot must be between 1 and league_size")
        self.league_size = league_size
        self.draft_slot = draft_slot

    def pick_for_round(self, round_number: int) -> int:
        round_number = int(round_number)
        if round_number < 1:
            raise ValueError("round_number must be at least 1")

        round_start = (round_number - 1) * self.league_size
        if round_number % 2 == 1:
            offset = self.draft_slot
        else:
            offset = self.league_size - self.draft_slot + 1
        return round_start + offset

    def next_pick_after(self, current_pick: int) -> int:
        current_pick = int(current_pick)
        if current_pick < 0:
            raise ValueError("current_pick must be non-negative")

        round_number = max(1, (current_pick // self.league_size) + 1)
        while True:
            user_pick = self.pick_for_round(round_number)
            if user_pick > current_pick:
                return user_pick
            round_number += 1

    @staticmethod
    def current_pick(*, drafted_count: int) -> int:
        drafted_count = int(drafted_count)
        if drafted_count < 0:
            raise ValueError("drafted_count must be non-negative")
        return drafted_count + 1
