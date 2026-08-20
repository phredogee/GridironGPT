from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_roster_advice_service import FantasyRosterAdviceService


def _player(position: str):
    return SimpleNamespace(position=position)


def test_empty_roster_summary_lists_all_starter_needs():
    advice = FantasyRosterAdviceService().build([])

    assert advice.summary == "Roster Needs: QB (1) · RB (2) · WR (2) · TE (1)"


def test_summary_updates_as_roster_fills():
    roster = [_player("QB"), _player("RB"), _player("RB"), _player("WR")]

    advice = FantasyRosterAdviceService().build(roster)

    assert advice.summary == "Roster Needs: WR (1) · TE (1)"


def test_filled_starters_have_completed_summary():
    roster = [_player("QB"), _player("RB"), _player("RB"), _player("WR"), _player("WR"), _player("TE")]

    advice = FantasyRosterAdviceService().build(roster)

    assert advice.summary == "Starter needs filled"


def test_badge_identifies_player_who_fills_active_need():
    advice = FantasyRosterAdviceService().build([_player("RB"), _player("RB")])

    assert advice.badge_for("WR") == "Fills WR need"
    assert advice.badge_for("RB") == ""
    assert advice.badge_for("K") == ""
