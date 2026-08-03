from datetime import datetime, timezone

import pytest

from gridiron_gpt.football_state.models.codex_entry import CodexEntry, CodexEntryType
from gridiron_gpt.football_state.repositories.codex_repository import JsonlCodexRepository
from gridiron_gpt.football_state.services.codex_context_service import CodexContextService


def entry(entry_type, day, summary, **overrides):
    values = {
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "entry_type": entry_type,
        "season": 2026,
        "summary": summary,
        "occurred_at": datetime(2026, 9, day, 12, 0, tzinfo=timezone.utc),
        "team": "ATL",
        "evidence": {"provider": "canonical"},
    }
    values.update(overrides)
    return CodexEntry(**values)


def test_codex_entry_round_trips():
    original = entry(CodexEntryType.ROLE_HISTORY, 1, "Opened season as starting RB")
    assert CodexEntry.from_dict(original.to_dict()) == original


def test_repository_is_append_only_and_deduplicates(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    item = entry(CodexEntryType.ROLE_HISTORY, 1, "Opened season as starting RB")
    assert repo.append(item) is True
    assert repo.append(item) is False
    assert len(repo.all()) == 1


def test_repository_queries_player_history_in_time_order(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.PRODUCTION_HISTORY, 20, "Week 3: 120 scrimmage yards"))
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 1, "Opened season as starting RB"))
    history = repo.for_player("bijan")
    assert [item.occurred_at.day for item in history] == [1, 20]


def test_repository_filters_by_history_type(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 1, "Starting RB"))
    repo.append(entry(CodexEntryType.AVAILABILITY_HISTORY, 2, "Limited in practice"))
    roles = repo.for_player("bijan", entry_type=CodexEntryType.ROLE_HISTORY)
    assert len(roles) == 1
    assert roles[0].summary == "Starting RB"


def test_latest_returns_latest_entry_of_requested_type(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 1, "Starter"))
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 8, "Three-down role"))
    assert repo.latest("bijan", CodexEntryType.ROLE_HISTORY).summary == "Three-down role"


def test_context_summary_combines_historical_dimensions(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 1, "Starter"))
    repo.append(entry(CodexEntryType.AVAILABILITY_HISTORY, 2, "Full participant"))
    repo.append(entry(CodexEntryType.PRODUCTION_HISTORY, 3, "100 scrimmage yards"))
    summary = CodexContextService(repo).summarize("bijan")
    assert summary["entry_count"] == 3
    assert summary["latest_role"] == "Starter"
    assert summary["latest_availability"] == "Full participant"
    assert summary["latest_production"] == "100 scrimmage yards"


def test_codex_can_span_multiple_seasons_and_teams(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.TEAM_HISTORY, 1, "Played for ATL", season=2025, team="ATL"))
    repo.append(entry(CodexEntryType.TEAM_HISTORY, 2, "Joined HOU", season=2026, team="HOU"))
    summary = CodexContextService(repo).summarize("bijan")
    assert summary["seasons"] == [2025, 2026]
    assert summary["teams"] == ["ATL", "HOU"]


def test_recent_returns_newest_first(tmp_path):
    repo = JsonlCodexRepository(tmp_path / "codex.jsonl")
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 1, "one"))
    repo.append(entry(CodexEntryType.ROLE_HISTORY, 2, "two"))
    recent = CodexContextService(repo).recent("bijan", limit=1)
    assert [item.summary for item in recent] == ["two"]


def test_recent_limit_must_be_positive(tmp_path):
    with pytest.raises(ValueError, match="positive"):
        CodexContextService(JsonlCodexRepository(tmp_path / "codex.jsonl")).recent("bijan", 0)
