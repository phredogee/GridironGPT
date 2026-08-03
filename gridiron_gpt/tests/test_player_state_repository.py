from datetime import datetime, timezone

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository
from gridiron_gpt.football_state.services.player_state_service import PlayerStateService


NOW = datetime(2026, 8, 3, 15, 0, tzinfo=timezone.utc)


def test_player_state_round_trip(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    state = CanonicalPlayerState(
        player_id="00-0036322",
        player_name="Bijan Robinson",
        team="ATL",
        position="RB",
        roster_status="ACT",
        identifiers={"gsis": "00-0036322", "espn": "4430807"},
        effective_at=NOW,
    )

    repository.save(state)
    loaded = repository.get("00-0036322")

    assert loaded == state


def test_repository_preserves_history_and_latest(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    first = CanonicalPlayerState(
        player_id="p1",
        player_name="Player One",
        team="ATL",
        position="RB",
        effective_at=NOW,
    )
    second = CanonicalPlayerState(
        player_id="p1",
        player_name="Player One",
        team="HOU",
        position="RB",
        effective_at=NOW,
    )

    repository.save(first)
    repository.save(second)

    assert repository.get("p1") == second
    assert repository.get_history("p1") == [first, second]
    assert repository.all_latest() == [second]


def test_service_promotes_catalog_rows_to_canonical_state(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")

    catalog = [{
        "player": "Bijan Robinson",
        "team": "ATL",
        "position": "RB",
        "status": "ACT",
        "depth_chart_position": "RB",
        "jersey_number": 7,
        "years_exp": 3,
        "college": "Texas",
        "rookie_year": 2023,
        "entry_year": 2023,
        "draft_club": "ATL",
        "draft_number": 8,
        "gsis_id": "00-0036322",
        "espn_id": 4430807,
        "sleeper_id": "9221",
        "pfr_id": "RobiBi01",
        "yahoo_id": None,
        "rotowire_id": 16684,
    }]

    service = PlayerStateService(
        repository,
        catalog_loader=lambda: catalog,
        clock=lambda: NOW,
    )

    states = service.refresh()

    assert len(states) == 1
    state = states[0]
    assert state.player_name == "Bijan Robinson"
    assert state.team == "ATL"
    assert state.roster_status == "ACT"
    assert state.identifiers["gsis"] == "00-0036322"
    assert state.identifiers["espn"] == "4430807"
    assert state.effective_at == NOW


def test_service_skips_rows_without_stable_identity(tmp_path):
    repository = JsonlPlayerStateRepository(tmp_path / "player_states.jsonl")
    service = PlayerStateService(
        repository,
        catalog_loader=lambda: [
            {"player": "No ID", "gsis_id": None},
            {"player": None, "gsis_id": "p2"},
        ],
        clock=lambda: NOW,
    )

    assert service.refresh() == []
    assert repository.all_latest() == []
