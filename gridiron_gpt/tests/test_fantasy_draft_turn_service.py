import pytest

from gridiron_gpt.draft.fantasy_draft_turn_service import FantasyDraftTurnService


def test_slot_eight_in_twelve_team_snake_has_expected_turns() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=8)

    assert service.pick_for_round(1) == 8
    assert service.pick_for_round(2) == 17
    assert service.pick_for_round(3) == 32
    assert service.pick_for_round(4) == 41


def test_first_slot_snakes_from_first_to_last() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=1)

    assert service.pick_for_round(1) == 1
    assert service.pick_for_round(2) == 24
    assert service.pick_for_round(3) == 25


def test_last_slot_snakes_with_back_to_back_turn() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=12)

    assert service.pick_for_round(1) == 12
    assert service.pick_for_round(2) == 13
    assert service.pick_for_round(3) == 36


def test_next_user_pick_from_current_overall_pick() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=8)

    assert service.next_pick_after(7) == 8
    assert service.next_pick_after(8) == 17
    assert service.next_pick_after(16) == 17
    assert service.next_pick_after(17) == 32


def test_current_pick_is_derived_from_drafted_count() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=8)

    assert service.current_pick(drafted_count=0) == 1
    assert service.current_pick(drafted_count=7) == 8
    assert service.current_pick(drafted_count=16) == 17


def test_invalid_league_size_is_rejected() -> None:
    with pytest.raises(ValueError, match="league_size"):
        FantasyDraftTurnService(league_size=1, draft_slot=1)


def test_invalid_draft_slot_is_rejected() -> None:
    with pytest.raises(ValueError, match="draft_slot"):
        FantasyDraftTurnService(league_size=12, draft_slot=13)


def test_negative_drafted_count_is_rejected() -> None:
    service = FantasyDraftTurnService(league_size=12, draft_slot=8)

    with pytest.raises(ValueError, match="drafted_count"):
        service.current_pick(drafted_count=-1)
