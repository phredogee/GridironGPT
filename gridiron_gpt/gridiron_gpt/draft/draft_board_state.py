from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class DraftOwnership(StrEnum):
    """Ownership recorded for a player removed from the live draft board."""

    OTHER_TEAM = "other_team"
    MY_TEAM = "my_team"


@dataclass(frozen=True)
class DraftedPlayer:
    """A drafted player plus the ownership needed for roster-aware advice."""

    player_id: str
    ownership: DraftOwnership = DraftOwnership.OTHER_TEAM


@dataclass
class DraftBoardState:
    """Ordered draft-day state shared by board and roster-aware features.

    The ordered list preserves existing Undo Last behavior while ownership
    distinguishes players selected by the user's team from the rest of the
    league. A player may only appear once on the board.
    """

    picks: list[DraftedPlayer] = field(default_factory=list)

    @classmethod
    def from_drafted_ids(cls, player_ids: list[str]) -> "DraftBoardState":
        """Create state compatible with the original drafted-ID session data."""

        state = cls()
        for player_id in player_ids:
            state.mark_drafted(player_id)
        return state

    @property
    def drafted_ids(self) -> list[str]:
        return [pick.player_id for pick in self.picks]

    @property
    def my_team_ids(self) -> list[str]:
        return [
            pick.player_id
            for pick in self.picks
            if pick.ownership is DraftOwnership.MY_TEAM
        ]

    def is_drafted(self, player_id: str) -> bool:
        return any(pick.player_id == player_id for pick in self.picks)

    def is_my_team(self, player_id: str) -> bool:
        return any(
            pick.player_id == player_id and pick.ownership is DraftOwnership.MY_TEAM
            for pick in self.picks
        )

    def mark_drafted(
        self,
        player_id: str,
        ownership: DraftOwnership = DraftOwnership.OTHER_TEAM,
    ) -> None:
        """Record a selection, updating ownership without changing pick order."""

        if not player_id:
            raise ValueError("player_id is required")

        for index, pick in enumerate(self.picks):
            if pick.player_id == player_id:
                if pick.ownership is not ownership:
                    self.picks[index] = DraftedPlayer(player_id, ownership)
                return

        self.picks.append(DraftedPlayer(player_id, ownership))

    def mark_my_team(self, player_id: str) -> None:
        self.mark_drafted(player_id, DraftOwnership.MY_TEAM)

    def restore(self, player_id: str) -> None:
        self.picks = [pick for pick in self.picks if pick.player_id != player_id]

    def undo_last(self) -> DraftedPlayer | None:
        if not self.picks:
            return None
        return self.picks.pop()

    def clear(self) -> None:
        self.picks.clear()
