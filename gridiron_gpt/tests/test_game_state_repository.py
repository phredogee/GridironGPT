from datetime import datetime, timezone

from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.repositories.jsonl_game_state_repository import (
    JsonlGameStateRepository,
)


NOW = datetime(2026, 8, 11, 14, 0, tzinfo=timezone.utc)
KICKOFF = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)


def test_game_state_round_trip(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    state = CanonicalGameState(
        game_id="2026_01_HOU_IND",
        season=2026,
        week=1,
        season_type="REG",
        home_team="IND",
        away_team="HOU",
        kickoff_at=KICKOFF,
        game_status="scheduled",
        venue="Lucas Oil Stadium",
        effective_at=NOW,
    )

    repository.save(state)

    assert repository.get("2026_01_HOU_IND") == state


def test_game_state_repository_preserves_history_and_latest(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "game_states.jsonl")
    first = CanonicalGameState(
        game_id="game-1",
        season=2026,
        week=1,
        season_type="REG",
        home_team="IND",
        away_team="HOU",
        kickoff_at=KICKOFF,
        game_status="scheduled",
        effective_at=NOW,
    )
    second = CanonicalGameState(
        game_id="game-1",
        season=2026,
        week=1,
        season_type="REG",
        home_team="IND",
        away_team="HOU",
        kickoff_at=KICKOFF,
        game_status="final",
        effective_at=NOW,
    )

    repository.save(first)
    repository.save(second)

    assert repository.get("game-1") == second
    assert repository.get_history("game-1") == [first, second]
    assert repository.all_latest() == [second]


def test_game_state_repository_returns_empty_for_missing_file(tmp_path):
    repository = JsonlGameStateRepository(tmp_path / "missing.jsonl")

    assert repository.get("missing") is None
    assert repository.get_history("missing") == []
    assert repository.all_latest() == []
