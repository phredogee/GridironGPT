from datetime import datetime, timezone
from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.propagation.propagation_planner import (
    PropagationPlanner,
)
from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantics,
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

def make_relationship(
    *,
    source_id: str,
    source_name: str,
    target_id: str,
    target_name: str,
    relationship_type: str,
    strength: float = 1.0,
    confidence: float = 1.0,
) -> EntityRelationship:
    now = datetime.now(timezone.utc).isoformat()

    return EntityRelationship(
        source_entity_id=source_id,
        source_entity_name=source_name,
        source_entity_type="player",
        target_entity_id=target_id,
        target_entity_name=target_name,
        target_entity_type="player",
        relationship_type=relationship_type,
        strength=strength,
        confidence=confidence,
        reason="Semantic planner test.",
        source_team="TST",
        target_team="TST",
        first_seen=now,
        last_updated=now,
    )


def test_semantic_path_multiplier_preserves_same_direction() -> None:
    semantics = RelationshipSemantics()

    class Relationship:
        relationship_type = "passes_to"

    planner = PropagationPlanner.__new__(PropagationPlanner)
    planner.relationship_semantics = semantics

    multiplier = planner.calculate_path_semantic_multiplier(
        relationships=[Relationship()],
        source_impact_score=-1.0,
    )

    assert multiplier == 0.85


def test_semantic_path_multiplier_reverses_competitor_signal() -> None:
    semantics = RelationshipSemantics()

    class Relationship:
        relationship_type = "competes_with"

    planner = PropagationPlanner.__new__(PropagationPlanner)
    planner.relationship_semantics = semantics

    multiplier = planner.calculate_path_semantic_multiplier(
        relationships=[Relationship()],
        source_impact_score=-1.0,
    )

    assert multiplier == -0.45


def test_multihop_semantics_carry_reversed_direction(
    tmp_path: Path,
) -> None:
    cortex = CortexFacade(data_directory=tmp_path)

    cortex.knowledge.save_relationship(
        make_relationship(
            source_id="starter",
            source_name="Starter",
            target_id="backup",
            target_name="Backup",
            relationship_type="competes_with",
        )
    )

    cortex.knowledge.save_relationship(
        make_relationship(
            source_id="backup",
            source_name="Backup",
            target_id="receiver",
            target_name="Receiver",
            relationship_type="passes_to",
        )
    )

    planner = PropagationPlanner(
        knowledge_graph=cortex.knowledge_graph,
    )

    candidates = planner.plan(
        source_entity_id="starter",
        max_depth=2,
        source_impact_score=-1.0,
    )

    candidates_by_id = {
        candidate.entity_id: candidate
        for candidate in candidates
    }

    backup = candidates_by_id["backup"]
    receiver = candidates_by_id["receiver"]

    # Starter decline benefits the competitor.
    assert backup.propagation_weight < 0

    # The receiver then moves in the same direction as the benefiting backup.
    assert receiver.propagation_weight < 0

    expected_receiver_weight = (
        1.0       # combined strength
        * 1.0     # combined confidence
        * -0.45   # competitor reversal; path multiplier remains negative
        * 0.65    # two-hop decay
    )

    assert abs(
        receiver.propagation_weight - expected_receiver_weight
    ) < 0.000001


def test_unknown_relationship_retains_legacy_path_weight(
    tmp_path: Path,
) -> None:
    cortex = CortexFacade(data_directory=tmp_path)

    cortex.knowledge.save_relationship(
        make_relationship(
            source_id="source",
            source_name="Source",
            target_id="target",
            target_name="Target",
            relationship_type="legacy_relationship",
            strength=0.85,
            confidence=0.95,
        )
    )

    planner = PropagationPlanner(
        knowledge_graph=cortex.knowledge_graph,
    )

    candidates = planner.plan(
        source_entity_id="source",
        max_depth=1,
        source_impact_score=1.0,
    )

    assert len(candidates) == 1

    assert abs(
        candidates[0].propagation_weight - 0.686375
    ) < 0.000001
