from __future__ import annotations

from types import SimpleNamespace
from typing import Mapping

from gridiron_gpt.draft.draft_board_state import DraftBoardState
from gridiron_gpt.draft.fantasy_position_run_service import (
    FantasyPositionRunService,
    PositionRunResult,
)


def build_position_run_from_draft_state(
    state: DraftBoardState,
    players_by_id: Mapping[str, object],
    *,
    window_size: int = 6,
) -> PositionRunResult:
    """Translate ordered draft picks into positional market-momentum input.

    Unknown player IDs are preserved as blank-position placeholders so the
    rolling pick window remains aligned with the actual draft sequence.
    """

    picks = []
    for drafted in state.picks:
        player = players_by_id.get(drafted.player_id)
        position = getattr(player, "position", None) if player is not None else None
        picks.append(SimpleNamespace(position=position))

    return FantasyPositionRunService(window_size=window_size).evaluate(picks)
