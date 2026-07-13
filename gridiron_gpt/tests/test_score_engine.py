from pathlib import Path

from gridiron_cortex.engine.score_engine import ScoreEngine
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.signal import Signal
from gridiron_cortex.storage.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)


def test_score_engine_applies_player_impact(tmp_path: Path):
    repository = JsonPlayerScorecardRepository(
        tmp_path / "player_scorecards.jsonl"
    )

    engine = ScoreEngine(repository=repository)

    entity = Entity(
        entity_type="player",
        name="Test Player",
        team="TST",
        confidence=1.0,
        source="test",
    )

    signal = Signal(
        headline="Test Player returns to practice.",
        entities=[entity],
        sentiment="positive",
        impact_score=1.0,
        positive_hits=["returns", "practice"],
        negative_hits=[],
        confidence=1.0,
        signal_type="news",
    )

    impacts = [
        Impact(
            entity_type="player",
            entity_name="Test Player",
            team="TST",
            impact_score=1.0,
            impact_type="direct",
            reason="Test direct impact.",
        )
    ]

    score_updates, scorecards, history = engine.apply(
        signal,
        impacts,
    )

    assert len(score_updates) == 1
    assert len(scorecards) == 1

    update = score_updates[0]
    scorecard = scorecards[0]

    assert update.entity_name == "Test Player"
    assert update.score_delta == 1.0
    assert update.previous_score == 50.0
    assert update.new_score == 51.0

    assert scorecard.player_id == "test_player"
    assert scorecard.overall_score == 51.0
    assert "test_player" in history
    assert len(history["test_player"]) == 1
