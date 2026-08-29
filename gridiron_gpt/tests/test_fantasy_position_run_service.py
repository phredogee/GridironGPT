from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_position_run_service import FantasyPositionRunService


def _pick(position: str):
    return SimpleNamespace(position=position)


def test_insufficient_history_reports_no_run() -> None:
    result = FantasyPositionRunService().evaluate([_pick("WR"), _pick("WR")])

    assert result.level == "none"
    assert result.position is None


def test_balanced_recent_picks_do_not_trigger_run() -> None:
    picks = [_pick("RB"), _pick("WR"), _pick("QB"), _pick("TE"), _pick("RB"), _pick("WR")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "none"
    assert result.position is None


def test_three_of_last_five_is_developing_run() -> None:
    picks = [_pick("RB"), _pick("WR"), _pick("WR"), _pick("QB"), _pick("WR")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "developing"
    assert result.position == "WR"
    assert result.position_count == 3
    assert result.window_size == 5


def test_four_of_last_six_is_active_run() -> None:
    picks = [_pick("RB"), _pick("WR"), _pick("WR"), _pick("QB"), _pick("WR"), _pick("WR")]

    result = FantasyPositionRunService().evaluate(picks)

    assert result.level == "active"
    assert result.position == "WR"
    assert result.position_count == 4
    assert result.window_size == 6


def test_only_recent_window_drives_run_detection() -> None:
    picks = [
        _pick("WR"), _pick("WR"), _pick("WR"),
        _pick("RB"), _pick("QB"), _pick("TE"), _pick("RB"), _pick("QB"),
    ]

    result = FantasyPositionRunService(window_size=5).evaluate(picks)

    assert result.level == "none"
    assert result.position is None


def test_result_explains_detected_run() -> None:
    picks = [_pick("RB"), _pick("WR"), _pick("WR"), _pick("QB"), _pick("WR")]

    result = FantasyPositionRunService().evaluate(picks)

    assert "3 of the last 5" in result.reason
    assert "WR" in result.reason
