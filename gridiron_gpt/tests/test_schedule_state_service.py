from datetime import datetime, timezone

import pytest

from gridiron_gpt.football_state.repositories.jsonl_game_state_repository import (
    JsonlGameStateRepository,
)
from gridiron_gpt.football_state.services.schedule_state_service import (
    ScheduleStateService,
)


NOW = datetime(2026, 8, 11, 14, 0, tzinfo=timezone.utc)


def _row(**overrides):
    row = {
        "game_id": "2026_01_HOU_DAL",
        "season": 2026,
        "game_type": "REG",
        "week": 1,
        "gameday": "2026-09-10",
        "gametime": "20:20",
        "away_team": "HOU",
        "home_team": "DAL",
        "stadium": "AT&T Stadium",
        "result": None,
    }
    row.update(overrides)
    return row


def test_schedule_service_promotes_rows_to_canonical_game_state(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: [_row()],
        clock=lambda: NOW,
    )

    states = service.refresh()

    assert len(states) == 1
    state = states[0]
    assert state.game_id == "2026_01_HOU_DAL"
    assert state.season == 2026
    assert state.week == 1
    assert state.season_type == "REG"
    assert state.away_team == "HOU"
    assert state.home_team == "DAL"
    assert state.venue == "AT&T Stadium"
    assert state.game_status == "scheduled"
    assert state.kickoff_at == datetime(2026, 9, 11, 0, 20, tzinfo=timezone.utc)
    assert repository.get(state.game_id) == state


def test_schedule_service_defaults_to_calendar_year_for_preseason_context(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: [],
        clock=lambda: NOW,
    )

    assert service.season == 2026


def test_schedule_service_accepts_explicit_season(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        season=2025,
        schedule_loader=lambda: [],
        clock=lambda: NOW,
    )

    assert service.season == 2025


def test_schedule_service_does_not_persist_unchanged_snapshot(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: [_row()],
        clock=lambda: NOW,
    )

    service.refresh()
    service.refresh()

    assert len(repository.get_history("2026_01_HOU_DAL")) == 1


def test_schedule_service_persists_meaningful_change(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    rows = [_row()]
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: rows,
        clock=lambda: NOW,
    )

    service.refresh()
    rows[0] = _row(gametime="20:30")
    service.refresh()

    history = repository.get_history("2026_01_HOU_DAL")
    assert len(history) == 2
    assert history[0].kickoff_at != history[1].kickoff_at


def test_schedule_service_marks_completed_game_final(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: [_row(result=7)],
        clock=lambda: NOW,
    )

    [state] = service.refresh()

    assert state.game_status == "final"


def test_schedule_service_skips_rows_without_stable_game_identity(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(
        repository,
        schedule_loader=lambda: [_row(game_id=None)],
        clock=lambda: NOW,
    )

    assert service.refresh() == []
    assert repository.all_latest() == []


def test_team_queries_return_next_game_and_week_context(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    rows = [
        _row(game_id="2026_01_BUF_HOU", away_team="BUF", home_team="HOU", gameday="2026-09-13", gametime="13:00"),
        _row(game_id="2026_02_HOU_KC", week=2, away_team="HOU", home_team="KC", gameday="2026-09-20", gametime="16:25"),
    ]
    service = ScheduleStateService(repository, schedule_loader=lambda: rows, clock=lambda: NOW)
    service.refresh()

    next_game = service.next_game_for_team("hou")
    week_two = service.game_for_team_week("HOU", 2)

    assert next_game is not None
    assert next_game.game_id == "2026_01_BUF_HOU"
    assert week_two is not None
    assert week_two.game_id == "2026_02_HOU_KC"
    assert service.is_bye_week("HOU", 3) is True
    assert service.is_bye_week("HOU", 2) is False


def test_bye_week_rejects_non_regular_season_week(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    service = ScheduleStateService(repository, schedule_loader=lambda: [], clock=lambda: NOW)

    with pytest.raises(ValueError):
        service.is_bye_week("HOU", 0)
