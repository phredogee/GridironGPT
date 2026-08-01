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

def test_injury_signal_changes_health_and_risk(
    tmp_path: Path,
):
    repository = JsonPlayerScorecardRepository(
        tmp_path / "player_scorecards.jsonl"
    )

    engine = ScoreEngine(repository=repository)

    signal = Signal(
        headline="Test Player ruled out with injury.",
        sentiment="negative",
        impact_score=-1.0,
        signal_category="injury",
    )

    impacts = [
        Impact(
            entity_type="player",
            entity_name="Test Player",
            team="TST",
            impact_score=-1.0,
            impact_type="direct",
            reason="Injury signal.",
        )
    ]

    _, scorecards, _ = engine.apply(signal, impacts)

    scorecard = scorecards[0]

    assert scorecard.overall_score == 49.0
    assert scorecard.opportunity_score == 49.4
    assert scorecard.health_score == 49.0
    assert scorecard.hype_score == 49.8
    assert scorecard.risk_score == 51.0
    assert scorecard.momentum_score == 49.5


def test_recovery_signal_improves_health_and_reduces_risk(
    tmp_path: Path,
):
    repository = JsonPlayerScorecardRepository(
        tmp_path / "player_scorecards.jsonl"
    )

    engine = ScoreEngine(repository=repository)

    signal = Signal(
        headline="Test Player returns as full participant.",
        sentiment="positive",
        impact_score=1.0,
        signal_category="recovery",
    )

    impacts = [
        Impact(
            entity_type="player",
            entity_name="Test Player",
            team="TST",
            impact_score=1.0,
            impact_type="direct",
            reason="Recovery signal.",
        )
    ]

    _, scorecards, _ = engine.apply(signal, impacts)

    scorecard = scorecards[0]

    assert scorecard.overall_score == 51.0
    assert scorecard.opportunity_score == 50.25
    assert scorecard.health_score == 51.0
    assert scorecard.hype_score == 50.5
    assert scorecard.risk_score == 49.3
    assert scorecard.momentum_score == 50.5


def test_opportunity_signal_primarily_changes_opportunity(
    tmp_path: Path,
):
    repository = JsonPlayerScorecardRepository(
        tmp_path / "player_scorecards.jsonl"
    )

    engine = ScoreEngine(repository=repository)

    signal = Signal(
        headline="Test Player taking first-team reps.",
        sentiment="positive",
        impact_score=1.0,
        signal_category="opportunity",
    )

    impacts = [
        Impact(
            entity_type="player",
            entity_name="Test Player",
            team="TST",
            impact_score=1.0,
            impact_type="direct",
            reason="First-team opportunity.",
        )
    ]

    _, scorecards, _ = engine.apply(signal, impacts)

    scorecard = scorecards[0]

    assert scorecard.overall_score == 51.0
    assert scorecard.opportunity_score == 51.0
    assert scorecard.health_score == 50.0
    assert scorecard.hype_score == 50.3
    assert scorecard.risk_score == 50.0
    assert scorecard.momentum_score == 50.5

def test_propagated_injury_impact_uses_category_profile(
    tmp_path: Path,
):
    repository = JsonPlayerScorecardRepository(
        tmp_path / "player_scorecards.jsonl"
    )

    engine = ScoreEngine(repository=repository)

    signal = Signal(
        headline="Starter ruled out with injury.",
        sentiment="negative",
        impact_score=-1.0,
        signal_category="injury",
    )

    impacts = [
        Impact(
            entity_type="player",
            entity_name="Related Player",
            team="TST",
            impact_score=-0.5,
            impact_type="propagated",
            reason="Propagated injury effect.",
            hop_count=1,
            relationship_strength=0.75,
            relationship_confidence=0.90,
            propagation_weight=0.50,
        )
    ]

    _, scorecards, _ = engine.apply(signal, impacts)

    scorecard = scorecards[0]

    assert scorecard.overall_score == 49.5
    assert scorecard.opportunity_score == 49.7
    assert scorecard.health_score == 49.5
    assert scorecard.hype_score == 49.9
    assert scorecard.risk_score == 50.5
    assert scorecard.momentum_score == 49.75
