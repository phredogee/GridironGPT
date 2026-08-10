from pathlib import Path
from datetime import datetime, timezone

from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAnalyzer,
)

def test_facade_processes_event(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline=(
            "Facade Test Player returns to practice "
            "with the first-team offense."
        ),
        source="facade_test",
        player="Facade Test Player",
        team="TST",
    )

    result = cortex.process_event(event)

    assert result.event == event
    assert result.signal is not None
    assert result.entities
    assert result.impacts
    assert result.score_updates
    assert result.player_scorecards
    assert result.recommendations


def test_facade_rejects_duplicate_event(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline="Duplicate Test Player returns to practice.",
        source="duplicate_test",
        player="Duplicate Test Player",
        team="TST",
    )

    first_result = cortex.process_event(event)
    second_result = cortex.process_event(event)

    assert first_result.signal is not None
    assert second_result.signal is None
    assert second_result.explanation == "Duplicate event ignored."


def test_facade_reads_player_scorecard(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline="Scorecard Test Player returns to practice.",
        source="scorecard_test",
        player="Scorecard Test Player",
        team="TST",
    )

    cortex.process_event(event)

    scorecard = cortex.get_player_scorecard(
        "scorecard_test_player"
    )

    assert scorecard is not None
    assert scorecard.player_name == "Scorecard Test Player"
    assert abs(scorecard.overall_score - 50.9) < 0.000001

def test_phase_b_end_to_end_reasoning_pipeline(
    tmp_path: Path,
):
    cortex = CortexFacade(data_directory=tmp_path)

    now = datetime.now(timezone.utc).isoformat()

    cortex.knowledge.save_relationship(
        EntityRelationship(
            source_entity_id="phase_b_qb",
            source_entity_name="Phase B QB",
            source_entity_type="player",
            target_entity_id="phase_b_receiver",
            target_entity_name="Phase B Receiver",
            target_entity_type="player",
            relationship_type="throws_to",
            strength=0.90,
            confidence=0.95,
            reason="Phase B end-to-end relationship.",
            source_team="TST",
            target_team="TST",
            first_seen=now,
            last_updated=now,
        )
    )

    event = RawEvent(
        headline=(
            "Phase B QB returns as a full participant "
            "with the first-team offense."
        ),
        source="phase_b_test",
        player="Phase B QB",
        team="TST",
    )

    result = cortex.process_event(event)

    # Signal interpretation
    assert result.signal is not None
    assert result.signal.impact_score > 0
    assert result.signal.signal_category == "recovery"

    # Direct + graph-propagated impacts
    direct = next(
        impact
        for impact in result.impacts
        if impact.impact_type == "direct"
    )

    propagated = next(
        impact
        for impact in result.impacts
        if impact.impact_type == "propagated"
    )

    assert direct.entity_name == "Phase B QB"
    assert propagated.entity_name == "Phase B Receiver"
    assert propagated.hop_count == 1
    assert propagated.propagation_weight is not None
    assert propagated.propagation_weight > 0

    # Both players reach multidimensional scoring
    scorecards = {
        scorecard.player_name: scorecard
        for scorecard in result.player_scorecards
    }

    assert "Phase B QB" in scorecards
    assert "Phase B Receiver" in scorecards

    qb = scorecards["Phase B QB"]
    receiver = scorecards["Phase B Receiver"]

    assert qb.health_score > 50.0
    assert qb.risk_score < 50.0

    assert receiver.health_score > 50.0
    assert receiver.risk_score < 50.0

    # Recommendation layer executes
    assert result.recommendations

    # Explanation layer preserves relationship reasoning
    propagated_chains = [
        chain
        for chain in result.evidence_chains
        if chain.entity_name == "Phase B Receiver"
    ]

    assert propagated_chains

    chain_text = " ".join(
        step.summary
        for step in propagated_chains[0].steps
    )

    assert "propagated impact" in chain_text
    assert "1-hop propagation" in chain_text
