from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.models.propagation import PropagationCandidate
from gridiron_gpt.intelligence.explorer_relationships import (
    build_propagation_rows,
    build_relationship_rows,
    find_entity_id,
)


def relationships():
    return [
        EntityRelationship(
            source_entity_id="qb-1",
            source_entity_name="Quarterback One",
            source_entity_type="player",
            target_entity_id="wr-1",
            target_entity_name="Receiver One",
            target_entity_type="player",
            relationship_type="throws_to",
            strength=0.9,
            confidence=0.8,
            reason="Primary passing relationship",
            source_team="AAA",
            target_team="AAA",
        ),
        EntityRelationship(
            source_entity_id="wr-2",
            source_entity_name="Receiver Two",
            source_entity_type="player",
            target_entity_id="wr-1",
            target_entity_name="Receiver One",
            target_entity_type="player",
            relationship_type="target_competitor",
            strength=0.7,
            confidence=0.9,
            reason="Competes for targets",
            source_team="AAA",
            target_team="AAA",
        ),
    ]


def test_find_entity_id_matches_source_or_target_name():
    rows = relationships()
    assert find_entity_id("Quarterback One", rows) == "qb-1"
    assert find_entity_id("receiver one", rows) == "wr-1"
    assert find_entity_id("Missing Player", rows) is None


def test_build_relationship_rows_preserves_direction_and_strength():
    rows = build_relationship_rows("wr-1", relationships())
    assert len(rows) == 2
    assert {row.direction for row in rows} == {"incoming"}
    assert {row.relationship_type for row in rows} == {
        "throws_to",
        "target_competitor",
    }


def test_build_propagation_rows_calculates_projected_impact():
    candidates = [
        PropagationCandidate(
            entity_id="wr-1",
            entity_name="Receiver One",
            entity_type="player",
            team="AAA",
            hop_count=1,
            relationship_strength=0.8,
            relationship_confidence=0.9,
            propagation_weight=-0.5,
            reason="QB --throws_to(-0.50)--> WR",
        ),
        PropagationCandidate(
            entity_id="rb-1",
            entity_name="Running Back One",
            entity_type="player",
            team="AAA",
            hop_count=2,
            relationship_strength=0.6,
            relationship_confidence=0.7,
            propagation_weight=0.2,
            reason="Two-hop path",
        ),
    ]

    rows = build_propagation_rows(candidates, source_impact=2.0)

    assert rows[0].entity_name == "Receiver One"
    assert rows[0].projected_impact == -1.0
    assert rows[1].projected_impact == 0.4
