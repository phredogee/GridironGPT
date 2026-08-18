from gridiron_gpt.draft.draft_board_state import (
    DraftBoardState,
    DraftOwnership,
)


def test_existing_drafted_ids_migrate_as_other_team_picks():
    state = DraftBoardState.from_drafted_ids(["player-1", "player-2"])

    assert state.drafted_ids == ["player-1", "player-2"]
    assert state.my_team_ids == []
    assert state.is_drafted("player-1") is True


def test_my_team_pick_is_drafted_and_added_to_my_roster():
    state = DraftBoardState()

    state.mark_my_team("player-1")

    assert state.drafted_ids == ["player-1"]
    assert state.my_team_ids == ["player-1"]
    assert state.is_my_team("player-1") is True


def test_existing_pick_can_be_reassigned_to_my_team_without_changing_order():
    state = DraftBoardState.from_drafted_ids(["player-1", "player-2"])

    state.mark_my_team("player-1")

    assert state.drafted_ids == ["player-1", "player-2"]
    assert state.my_team_ids == ["player-1"]


def test_existing_my_team_pick_can_be_reassigned_to_other_team():
    state = DraftBoardState()
    state.mark_my_team("player-1")

    state.mark_drafted("player-1", DraftOwnership.OTHER_TEAM)

    assert state.drafted_ids == ["player-1"]
    assert state.my_team_ids == []


def test_restore_removes_player_from_board_and_my_team():
    state = DraftBoardState()
    state.mark_my_team("player-1")
    state.mark_drafted("player-2")

    state.restore("player-1")

    assert state.drafted_ids == ["player-2"]
    assert state.my_team_ids == []


def test_undo_last_preserves_draft_order_semantics():
    state = DraftBoardState()
    state.mark_my_team("player-1")
    state.mark_drafted("player-2")

    removed = state.undo_last()

    assert removed is not None
    assert removed.player_id == "player-2"
    assert state.drafted_ids == ["player-1"]
    assert state.my_team_ids == ["player-1"]


def test_clear_resets_draft_and_my_team_state():
    state = DraftBoardState()
    state.mark_my_team("player-1")
    state.mark_drafted("player-2")

    state.clear()

    assert state.drafted_ids == []
    assert state.my_team_ids == []


def test_empty_player_id_is_rejected():
    state = DraftBoardState()

    try:
        state.mark_drafted("")
    except ValueError as exc:
        assert str(exc) == "player_id is required"
    else:
        raise AssertionError("expected empty player_id to be rejected")
