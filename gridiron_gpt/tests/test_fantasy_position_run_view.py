from gridiron_gpt.draft.fantasy_position_run_service import PositionRunResult
from gridiron_gpt.draft.fantasy_position_run_view import build_position_run_display


def _result(*, level: str, position: str | None, count: int, window: int):
    return PositionRunResult(
        level=level,
        position=position,
        position_count=count,
        window_size=window,
        reason="domain explanation",
    )


def test_active_run_has_concise_pressure_message() -> None:
    display = build_position_run_display(
        _result(level="active", position="WR", count=4, window=6)
    )

    assert display is not None
    assert display.headline == "ACTIVE WR RUN"
    assert display.detail == "4 of the last 6 picks were WR."
    assert display.guidance == "Market momentum is increasing pressure at WR."


def test_developing_run_has_cautious_message() -> None:
    display = build_position_run_display(
        _result(level="developing", position="RB", count=3, window=5)
    )

    assert display is not None
    assert display.headline == "DEVELOPING RB RUN"
    assert display.detail == "3 of the last 5 picks were RB."
    assert display.guidance == "A positional run may be forming."


def test_no_run_is_hidden_to_avoid_draft_assistant_clutter() -> None:
    display = build_position_run_display(
        _result(level="none", position=None, count=2, window=6)
    )

    assert display is None
