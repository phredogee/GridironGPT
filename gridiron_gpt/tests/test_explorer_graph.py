from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_gpt.intelligence.explorer_graph import build_explorer_graph


def relationship(source, target, rel_type, strength, confidence, active=True):
    return EntityRelationship(
        source_entity_id=source,
        source_entity_name=source.upper(),
        source_entity_type="player",
        target_entity_id=target,
        target_entity_name=target.upper(),
        target_entity_type="player",
        relationship_type=rel_type,
        strength=strength,
        confidence=confidence,
        source_team="AAA",
        target_team="AAA",
        active=active,
    )


def test_explorer_graph_keeps_only_root_connections():
    graph = build_explorer_graph(
        "qb",
        [
            relationship("qb", "wr", "throws_to", 0.9, 0.9),
            relationship("rb", "qb", "backs_up", 0.7, 0.8),
            relationship("wr", "te", "target_competitor", 0.8, 0.8),
        ],
    )

    assert {node.entity_id for node in graph.nodes} == {"qb", "wr", "rb"}
    assert len(graph.edges) == 2
    assert sum(node.is_root for node in graph.nodes) == 1


def test_explorer_graph_ignores_inactive_relationships():
    graph = build_explorer_graph(
        "qb",
        [
            relationship("qb", "wr", "throws_to", 0.9, 0.9, active=False),
        ],
    )

    assert graph.nodes == ()
    assert graph.edges == ()


def test_explorer_graph_limits_neighbors_by_relationship_quality():
    graph = build_explorer_graph(
        "root",
        [
            relationship("root", "a", "throws_to", 0.9, 0.9),
            relationship("root", "b", "throws_to", 0.8, 0.8),
            relationship("root", "c", "throws_to", 0.2, 0.2),
        ],
        max_neighbors=2,
    )

    assert {node.entity_id for node in graph.nodes} == {"root", "a", "b"}
    assert [edge.target_id for edge in graph.edges] == ["a", "b"]
