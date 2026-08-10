from datetime import datetime, timezone

import pytest

from gridiron_gpt.football_state.models.game_context import (
    CanonicalGameContext,
    GameStatus,
    VenueSide,
)
from gridiron_gpt.football_state.services.schedule_context_service import ScheduleContextService


def game(week, home, away, day, status=GameStatus.SCHEDULED, **overrides):
    values = {
        "game_id": f"2026_{week:02d}_{away}_{home}",
        "season": 2026,
        "week": week,
        "season_type": "REG",
        "home_team": home,
        "away_team": away,
        "kickoff_at": datetime(2026, 9, day, 17, 0, tzinfo=timezone.utc),
        "status": status,
    }
    values.update(overrides)
    return CanonicalGameContext(**values)


def test_resolves_current_week_opponent_and_venue():
    games = [game(3, "ATL", "TB", 20)]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.opponent == "TB"
    assert result.venue_side == VenueSide.HOME
    assert result.bye_week is False


def test_resolves_away_game():
    games = [game(3, "TB", "ATL", 20)]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.opponent == "TB"
    assert result.venue_side == VenueSide.AWAY


def test_missing_current_week_with_later_game_is_bye():
    games = [
        game(3, "ATL", "TB", 20, status=GameStatus.FINAL),
        game(5, "CAR", "ATL", 30),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 4, games)

    assert result.bye_week is True
    assert result.next_game.week == 5
    assert result.opponent == "CAR"


def test_partial_schedule_end_is_not_assumed_to_be_bye():
    games = [game(3, "ATL", "TB", 20, status=GameStatus.FINAL)]

    result = ScheduleContextService().resolve("ATL", 2026, 4, games)

    assert result.bye_week is False
    assert result.next_game is None


def test_rest_window_is_calculated_between_completed_and_next_game():
    games = [
        game(2, "ATL", "NO", 13, status=GameStatus.FINAL),
        game(3, "TB", "ATL", 20),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.days_rest == 7.0
    assert result.short_rest is False
    assert result.extended_rest is False


def test_short_rest_is_identified():
    games = [
        game(2, "ATL", "NO", 15, status=GameStatus.FINAL),
        game(3, "TB", "ATL", 20),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.days_rest == 5.0
    assert result.short_rest is True


def test_extended_rest_after_bye_is_identified():
    games = [
        game(3, "ATL", "TB", 10, status=GameStatus.FINAL),
        game(5, "CAR", "ATL", 24),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 4, games)

    assert result.days_rest == 14.0
    assert result.extended_rest is True


def test_canceled_game_is_not_selected_as_next_game():
    games = [
        game(3, "ATL", "TB", 20, status=GameStatus.CANCELED),
        game(4, "CAR", "ATL", 27),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.next_game.week == 4
    assert result.opponent == "CAR"


def test_other_teams_and_seasons_are_ignored():
    games = [
        game(3, "DAL", "NYG", 20),
        game(3, "ATL", "TB", 20, season=2025, game_id="2025_03_TB_ATL"),
        game(3, "ATL", "NO", 20),
    ]

    result = ScheduleContextService().resolve("ATL", 2026, 3, games)

    assert result.opponent == "NO"


def test_invalid_inputs_are_rejected():
    service = ScheduleContextService()

    with pytest.raises(ValueError, match="team"):
        service.resolve("", 2026, 3, [])
    with pytest.raises(ValueError, match="season"):
        service.resolve("ATL", 0, 3, [])
    with pytest.raises(ValueError, match="as_of_week"):
        service.resolve("ATL", 2026, 0, [])
