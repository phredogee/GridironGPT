from types import SimpleNamespace

import pytest

from gridiron_gpt.draft.fantasy_roster_needs_service import FantasyRosterNeedsService


def _player(position: str):
    return SimpleNamespace(position=position)


def test_empty_roster_needs_all_starter_positions():
    service = FantasyRosterNeedsService()

    needs = service.evaluate([])

    assert needs["QB"].deficit == 1
    assert needs["RB"].deficit == 2
    assert needs["WR"].deficit == 2
    assert needs["TE"].deficit == 1
    assert service.needed_positions([]) == ("QB", "RB", "WR", "TE")


def test_filled_position_is_removed_from_needed_positions():
    service = FantasyRosterNeedsService()
    roster = [_player("RB"), _player("RB"), _player("WR")]

    needs = service.evaluate(roster)

    assert needs["RB"].filled is True
    assert needs["WR"].deficit == 1
    assert service.needed_positions(roster) == ("QB", "WR", "TE")


def test_extra_players_do_not_create_negative_deficit():
    service = FantasyRosterNeedsService()
    roster = [_player("QB"), _player("QB"), _player("QB")]

    need = service.need_for("qb", roster)

    assert need is not None
    assert need.current == 3
    assert need.target == 1
    assert need.deficit == 0
    assert need.filled is True


def test_unknown_positions_do_not_affect_known_needs():
    service = FantasyRosterNeedsService()

    needs = service.evaluate([_player("K"), _player("DST"), _player("")])

    assert needs["QB"].current == 0
    assert needs["RB"].current == 0
    assert needs["WR"].current == 0
    assert needs["TE"].current == 0


def test_custom_targets_are_supported():
    service = FantasyRosterNeedsService({"QB": 1, "RB": 3, "WR": 3, "TE": 0})
    roster = [_player("RB"), _player("WR"), _player("WR")]

    needs = service.evaluate(roster)

    assert needs["RB"].deficit == 2
    assert needs["WR"].deficit == 1
    assert needs["TE"].filled is True
    assert service.needed_positions(roster) == ("QB", "RB", "WR")


def test_negative_target_is_rejected():
    with pytest.raises(ValueError, match="roster targets cannot be negative"):
        FantasyRosterNeedsService({"RB": -1})
