from datetime import datetime, timezone
from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.propagation.propagation_planner import (
    PropagationPlanner,
)


def test_hop_decay():
    assert PropagationPlanner.hop_decay(0) == 1.0
    assert PropagationPlanner.hop_decay(1) == 0.85
    assert PropagationPlanner.hop_decay(2) == 0.65
    assert PropagationPlanner.hop_decay(3) == 0.40
    assert PropagationPlanner.hop_decay(4) == 0.20


def test_weight_calculation():
    weight = PropagationPlanner.calculate_weight(
        strength=0.85,
        confidence=0.95,
        hops=1,
    )

    assert abs(weight - 0.686375) < 0.000001


def test_planner_creates_candidate(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    now = datetime.now(timezone.utc).isoformat()

    cortex.knowledge.save_relationship(
        EntityRelationship(
            source_entity_id="test_qb",
            source_entity_name="Test QB",
            source_entity_type="player",
            target_entity_id="test_receiver",
            target_entity_name="Test Receiver",
            target_entity_type="player",
            relationship_type="quarterback_receiver",
            strength=0.85,
            confidence=0.95,
            reason="Test quarterback and receiver relationship.",
            source_team="TST",
            target_team="TST",
            first_seen=now,
            last_updated=now,
        )
    )

    planner = PropagationPlanner(
        knowledge_graph=cortex.knowledge_graph,
    )

    candidates = planner.plan(
        source_entity_id="test_qb",
        max_depth=2,
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.entity_id == "test_receiver"
    assert candidate.entity_name == "Test Receiver"
    assert candidate.hop_count == 1
    assert candidate.relationship_strength == 0.85
    assert candidate.relationship_confidence == 0.95
    assert abs(
        candidate.propagation_weight - 0.686375
    ) < 0.000001
