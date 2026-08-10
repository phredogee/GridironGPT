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
        "depth_chart_position": "RB1",
        "effective_at": NOW,
    }
    values.update(overrides)
    return CanonicalPlayerState(**values)


def test_detects_team_status_depth_and_position_changes():
    previous = state()
    current = state(
        team="HOU",
        position="WR",
        roster_status="RES",
        depth_chart_position="WR2",
    )

    change = PlayerStateService.detect_change(previous, current)

    assert change.meaningful_change is True
    assert change.team_changed is True
    assert change.position_changed is True
    assert change.roster_status_changed is True
    assert change.depth_chart_changed is True
    assert change.changed_fields["team"] == ("ATL", "HOU")


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


def test_refresh_persists_meaningful_change_and_exposes_it(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    catalogs = iter([
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
            "depth_chart_position": "RB2",
        }],
        [{
            "gsis_id": "00-0039876",
            "player": "Example Player",
            "team": "ATL",
            "position": "RB",
            "status": "ACT",
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
