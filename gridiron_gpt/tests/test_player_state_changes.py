from datetime import datetime, timezone

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import (
    JsonlPlayerStateRepository,
)
from gridiron_gpt.football_state.services.player_state_service import PlayerStateService


NOW = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)


def state(**overrides):
    values = {
        "player_id": "00-0039876",
        "player_name": "Example Player",
        "team": "ATL",
        "position": "RB",
        "roster_status": "ACT",
        "status_description_abbr": "A01",
        "roster_week": 1,
        "roster_game_type": "REG",
        "depth_chart_position": "RB1",
        "effective_at": NOW,
    }
    values.update(overrides)
    return CanonicalPlayerState(**values)


def test_detects_team_status_detail_depth_and_position_changes():
    previous = state()
    current = state(
        team="HOU",
        position="WR",
        roster_status="RES",
        status_description_abbr="R01",
        depth_chart_position="WR2",
    )

    change = PlayerStateService.detect_change(previous, current)

    assert change.meaningful_change is True
    assert change.team_changed is True
    assert change.position_changed is True
    assert change.roster_status_changed is True
    assert change.depth_chart_changed is True
    assert change.changed_fields["team"] == ("ATL", "HOU")
    assert change.changed_fields["status_description_abbr"] == ("A01", "R01")


def test_week_and_game_type_are_context_not_meaningful_changes():
    previous = state(roster_week=1, roster_game_type="PRE")
    current = state(roster_week=2, roster_game_type="REG")

    change = PlayerStateService.detect_change(previous, current)

    assert change.meaningful_change is False
    assert change.changed_fields == {}


def test_identical_state_is_not_meaningful_change():
    previous = state()
    current = state(effective_at=datetime(2026, 8, 3, 19, 0, tzinfo=timezone.utc))

    change = PlayerStateService.detect_change(previous, current)

    assert change.meaningful_change is False
    assert change.changed_fields == {}


def test_refresh_does_not_persist_duplicate_snapshot(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    catalog = [{
        "gsis_id": "00-0039876",
        "player": "Example Player",
        "team": "ATL",
        "position": "RB",
        "status": "ACT",
        "status_description_abbr": "A01",
        "week": 1,
        "game_type": "REG",
        "depth_chart_position": "RB1",
    }]
    service = PlayerStateService(
        repository,
        catalog_loader=lambda: catalog,
        clock=lambda: NOW,
    )

    service.refresh()
    service.refresh()

    history = repository.get_history("00-0039876")
    assert len(history) == 1
    assert service.last_changes == []
    assert history[0].status_description_abbr == "A01"
    assert history[0].roster_week == 1
    assert history[0].roster_game_type == "REG"


def test_refresh_persists_meaningful_change_and_exposes_it(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    catalogs = iter([
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
            "status_description_abbr": "A01",
            "depth_chart_position": "RB2",
        }],
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
            "status_description_abbr": "A01",
            "depth_chart_position": "RB1",
        }],
    ])
    moments = iter([
        NOW,
        datetime(2026, 8, 4, 18, 0, tzinfo=timezone.utc),
    ])
    service = PlayerStateService(
        repository,
        catalog_loader=lambda: next(catalogs),
        clock=lambda: next(moments),
    )

    service.refresh()
    changes = service.refresh_changes()

    assert len(changes) == 1
    assert changes[0].depth_chart_changed is True
    assert changes[0].changed_fields["depth_chart_position"] == ("RB2", "RB1")
    assert len(repository.get_history("00-0039876")) == 2


def test_refresh_persists_status_detail_change(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    catalogs = iter([
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
            "status_description_abbr": "A01",
            "depth_chart_position": "RB1",
        }],
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
            "status_description_abbr": "A02",
            "depth_chart_position": "RB1",
        }],
    ])
    service = PlayerStateService(repository, catalog_loader=lambda: next(catalogs), clock=lambda: NOW)

    service.refresh()
    changes = service.refresh_changes()

    assert len(changes) == 1
    assert changes[0].changed_fields["status_description_abbr"] == ("A01", "A02")
    assert len(repository.get_history("00-0039876")) == 2
