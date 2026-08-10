import pytest

from gridiron_gpt.fantasy_decisions.models import (
    DecisionType,
    FantasyDecision,
    RecommendationAction,
)
from gridiron_gpt.fantasy_decisions.repository import JsonlFantasyDecisionRepository


def decision(name="Bijan Robinson"):
    return FantasyDecision(
        decision_type=DecisionType.START_SIT,
        action=RecommendationAction.START,
        player_id="bijan",
        player_name=name,
        score=18.5,
        confidence=0.88,
        summary=f"Start {name}",
        reasons=("High projected workload",),
        metadata={"week": 4},
    )


def test_repository_appends_and_reads_decisions(tmp_path):
    repo = JsonlFantasyDecisionRepository(tmp_path / "decisions.jsonl")
    repo.append(decision())
    records = repo.all()
    assert len(records) == 1
    assert records[0]["action"] == "start"
    assert records[0]["decision_type"] == "start_sit"


def test_repository_preserves_history(tmp_path):
    repo = JsonlFantasyDecisionRepository(tmp_path / "decisions.jsonl")
    repo.append(decision("One"))
    repo.append(decision("Two"))
    assert [item["player_name"] for item in repo.all()] == ["One", "Two"]


def test_latest_returns_requested_tail(tmp_path):
    repo = JsonlFantasyDecisionRepository(tmp_path / "decisions.jsonl")
    repo.append(decision("One"))
    repo.append(decision("Two"))
    assert [item["player_name"] for item in repo.latest(1)] == ["Two"]


def test_latest_limit_must_be_positive(tmp_path):
    with pytest.raises(ValueError, match="positive"):
        JsonlFantasyDecisionRepository(tmp_path / "decisions.jsonl").latest(0)
