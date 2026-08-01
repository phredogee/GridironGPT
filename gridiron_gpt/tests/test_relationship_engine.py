from datetime import datetime, timezone
from pathlib import Path

from gridiron_cortex.engine.relationship_engine import RelationshipEngine
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.models.signal import Signal
from gridiron_cortex.reason.relationship_engine import RelationshipEngine
from gridiron_cortex.remember.json_relationship_repository import (
    JsonRelationshipRepository,
)

def test_relationship_engine_creates_direct_and_propagated_impacts(
    tmp_path: Path,
):
    repository = JsonRelationshipRepository(
        tmp_path / "relationships.jsonl"
    )

    now = datetime.now(timezone.utc).isoformat()

    repository.save(
        EntityRelationship(
            source_entity_id="test_qb",
            source_entity_name="Test QB",
            source_entity_type="player",
            target_entity_id="test_receiver",
            target_entity_name="Test Receiver",
            target_entity_type="player",
            relationship_type="quarterback_receiver",
            strength=0.80,
            confidence=0.90,
            reason="Test quarterback and receiver relationship.",
            source_team="TST",
            target_team="TST",
            first_seen=now,
            last_updated=now,
        )
    )

    engine = RelationshipEngine(repository=repository)

    entity = Entity(
        entity_type="player",
        name="Test QB",
        team="TST",
        confidence=1.0,
        source="test",
    )

    signal = Signal(
        headline="Test QB returns to practice.",
        entities=[entity],
        sentiment="positive",
        impact_score=1.0,
        positive_hits=["returns", "practice"],
        negative_hits=[],
        confidence=1.0,
        signal_type="news",
    )

    impacts = engine.propagate(signal)

    assert len(impacts) == 2

    direct = next(
        impact
        for impact in impacts
        if impact.impact_type == "direct"
    )

    propagated = next(
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    )

    assert direct.entity_name == "Test QB"
    assert direct.impact_score == 1.0

    assert propagated.entity_name == "Test Receiver"
    assert abs(propagated.impact_score - 0.72) < 0.000001

def test_relationship_engine_uses_propagation_planner(
    tmp_path: Path,
):
    from gridiron_cortex.facade import CortexFacade

    cortex = CortexFacade(data_directory=tmp_path)

    now = datetime.now(timezone.utc).isoformat()

    cortex.knowledge.save_relationship(
        EntityRelationship(
            source_entity_id="planner_qb",
            source_entity_name="Planner QB",
            source_entity_type="player",
            target_entity_id="planner_receiver",
            target_entity_name="Planner Receiver",
            target_entity_type="player",
            relationship_type="quarterback_receiver",
            strength=0.85,
            confidence=0.95,
            reason="Planner integration test.",
            source_team="TST",
            target_team="TST",
            first_seen=now,
            last_updated=now,
        )
    )

    entity = Entity(
        entity_type="player",
        name="Planner QB",
        team="TST",
        confidence=1.0,
        source="test",
    )

    signal = Signal(
        headline="Planner QB returns to the first-team offense.",
        entities=[entity],
        sentiment="positive",
        impact_score=1.0,
        positive_hits=["returns", "first-team"],
        negative_hits=[],
        confidence=1.0,
        signal_type="news",
    )

    impacts = cortex.engine.relationship_engine.propagate(signal)

    propagated = next(
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    )

    assert propagated.entity_name == "Planner Receiver"

    assert abs(
        propagated.impact_score - 0.686375
    ) < 0.000001

    assert propagated.hop_count == 1

    assert abs(
        propagated.relationship_strength - 0.85
    ) < 0.000001

    assert abs(
        propagated.relationship_confidence - 0.95
    ) < 0.000001

    assert abs(
        propagated.propagation_weight - 0.686375
    ) < 0.000001


def make_signal(
    impact_score: float,
    player_name: str = "CJ Stroud",
) -> Signal:
    return Signal(
        headline=f"Test signal for {player_name}",
        sentiment="positive" if impact_score > 0 else "negative",
        impact_score=impact_score,
        entities=[
            Entity(
                entity_type="player",
                name=player_name,
                team="HOU",
            )
        ],
    )

def save_relationship(
    repository,
    relationship_type: str,
) -> None:
    repository.save(
        EntityRelationship(
            source_entity_id="cj_stroud",
            source_entity_name="CJ Stroud",
            source_entity_type="player",
            target_entity_id="tank_dell",
            target_entity_name="Tank Dell",
            target_entity_type="player",
            relationship_type=relationship_type,
            strength=1.0,
            confidence=1.0,
            reason="Test relationship.",
            source_team="HOU",
            target_team="HOU",
        )
    )


def test_passes_to_preserves_positive_direction(tmp_path) -> None:
    repository = JsonRelationshipRepository(
        tmp_path / "relationships.jsonl"
    )

    save_relationship(
        repository,
        relationship_type="passes_to",
    )

    engine = RelationshipEngine(repository=repository)

    impacts = engine.propagate(
        make_signal(impact_score=1.0)
    )

    propagated = [
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    ]

    assert len(propagated) == 1
    assert propagated[0].entity_name == "Tank Dell"
    assert propagated[0].impact_score == 1.0


def test_competes_with_reverses_positive_direction(tmp_path) -> None:
    repository = JsonRelationshipRepository(
        tmp_path / "relationships.jsonl"
    )

    save_relationship(
        repository,
        relationship_type="competes_with",
    )

    engine = RelationshipEngine(repository=repository)

    impacts = engine.propagate(
        make_signal(impact_score=1.0)
    )

    propagated = [
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    ]

    assert len(propagated) == 1
    assert propagated[0].impact_score == -0.45


def test_competes_with_reverses_negative_direction(tmp_path) -> None:
    repository = JsonRelationshipRepository(
        tmp_path / "relationships.jsonl"
    )

    save_relationship(
        repository,
        relationship_type="competes_with",
    )

    engine = RelationshipEngine(repository=repository)

    impacts = engine.propagate(
        make_signal(impact_score=-1.0)
    )

    propagated = [
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    ]

    assert len(propagated) == 1
    assert propagated[0].impact_score == 0.45


def test_unknown_relationship_preserves_legacy_behavior(
    tmp_path,
) -> None:
    repository = JsonRelationshipRepository(
        tmp_path / "relationships.jsonl"
    )

    save_relationship(
        repository,
        relationship_type="unknown_relationship",
    )

    engine = RelationshipEngine(repository=repository)

    impacts = engine.propagate(
        make_signal(impact_score=1.0)
    )

    propagated = [
        impact
        for impact in impacts
        if impact.impact_type == "propagated"
    ]

    assert len(propagated) == 1
    assert propagated[0].impact_score == 1.0
