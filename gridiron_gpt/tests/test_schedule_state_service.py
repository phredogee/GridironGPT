from datetime import datetime, timezone

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
