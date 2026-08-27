from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_position_run_service import FantasyPositionRunService


def _pick(position):
    return SimpleNamespace(position=position)


def test_two_positions_tied_for_lead_does_not_claim_a_run() -> None:
    picks = [_pick("RB"), _pick("WR"), _pick("RB"), _pick("WR"), _pick("QB"), _pick("TE")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "none"
    assert result.position is None


def test_missing_positions_do_not_create_false_run() -> None:
    picks = [_pick(None), _pick(""), _pick("WR"), _pick(None), _pick("RB"), _pick("QB")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "none"
    assert result.position is None


def test_run_decays_when_older_same_position_picks_leave_window() -> None:
    service = FantasyPositionRunService(window_size=5)
    active = [_pick("WR"), _pick("WR"), _pick("QB"), _pick("WR"), _pick("WR")]
    decayed = active + [_pick("RB"), _pick("TE"), _pick("QB")]

    before = service.evaluate(active)
    after = service.evaluate(decayed)

    assert before.level == "active"
    assert before.position == "WR"
    assert after.level == "none"
    assert after.position is None


def test_position_matching_is_normalized() -> None:
    picks = [_pick("wr"), _pick("WR"), _pick(" Wr "), _pick("QB"), _pick("RB")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "developing"
    assert result.position == "WR"


def test_custom_window_still_uses_concentration_not_raw_history() -> None:
    service = FantasyPositionRunService(window_size=7)
    picks = [
        _pick("RB"), _pick("WR"), _pick("WR"), _pick("QB"),
        _pick("WR"), _pick("TE"), _pick("WR"),
    ]

    result = service.evaluate(picks)

    assert result.level == "developing"
    assert result.position == "WR"
    assert result.position_count == 4
    assert result.window_size == 7
