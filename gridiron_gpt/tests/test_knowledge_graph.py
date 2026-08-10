from datetime import datetime, timezone
from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.entity_relationship import EntityRelationship


def save_relationship(
    cortex,
    source_id: str,
    source_name: str,
    target_id: str,
    target_name: str,
    strength: float,
    confidence: float,
):
    now = datetime.now(timezone.utc).isoformat()

    cortex.knowledge.save_relationship(
        EntityRelationship(
            source_entity_id=source_id,
            source_entity_name=source_name,
            source_entity_type="player",
            target_entity_id=target_id,
            target_entity_name=target_name,
            target_entity_type="player",
            relationship_type="test_relationship",
            strength=strength,
            confidence=confidence,
            reason="Knowledge graph test relationship.",
            source_team="TST",
            target_team="TST",
            first_seen=now,
            last_updated=now,
        )
    )


def test_graph_builds_one_hop_relationship(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    save_relationship(
        cortex,
        "player_a",
        "Player A",
        "player_b",
        "Player B",
        0.80,
        0.90,
    )

    graph = cortex.get_entity_graph(
        "player_a",
        max_depth=1,
    )

    node_ids = {node.entity_id for node in graph.nodes}

    assert node_ids == {"player_a", "player_b"}
    assert len(graph.edges) == 1


def test_graph_finds_two_hop_path(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    save_relationship(
        cortex,
        "player_a",
        "Player A",
        "player_b",
        "Player B",
        0.80,
        0.90,
    )

    save_relationship(
        cortex,
        "player_b",
        "Player B",
        "player_c",
        "Player C",
        0.70,
        0.85,
    )

    paths = cortex.find_relationship_paths(
        source_entity_id="player_a",
        target_entity_id="player_c",
        max_depth=3,
    )

    assert len(paths) == 1

    path = paths[0]

    assert path.hop_count == 2
    assert abs(path.combined_strength - 0.56) < 0.000001
    assert abs(path.combined_confidence - 0.765) < 0.000001
