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


def test_explorer_graph_attaches_propagated_intelligence_to_nodes():
    graph = build_explorer_graph(
        "qb",
        [relationship("qb", "wr", "throws_to", 0.9, 0.9)],
        impact_by_entity={"wr": 0.62},
        weight_by_entity={"wr": 0.31},
        hops_by_entity={"wr": 1},
        path_by_entity={"wr": "QB --throws_to(+1.00)--> WR"},
        source_impact=2.0,
        seed_headline="Quarterback returns to full practice",
    )

    wr = next(node for node in graph.nodes if node.entity_id == "wr")
    assert wr.projected_impact == 0.62
    assert wr.propagation_weight == 0.31
    assert wr.hop_count == 1
    assert wr.evidence_path == "QB --throws_to(+1.00)--> WR"
    assert graph.source_impact == 2.0
    assert graph.seed_headline == "Quarterback returns to full practice"


def test_explorer_graph_edges_expose_current_projected_effect():
    graph = build_explorer_graph(
        "root",
        [
            relationship("root", "positive", "throws_to", 0.9, 0.9),
            relationship("negative", "root", "target_competitor", 0.8, 0.8),
        ],
        impact_by_entity={"positive": 0.5, "negative": -0.4},
    )

    impacts = {edge.projected_impact for edge in graph.edges}
    assert impacts == {0.5, -0.4}


def test_explorer_graph_remains_backward_compatible_without_intelligence():
    graph = build_explorer_graph(
        "qb",
        [relationship("qb", "wr", "throws_to", 0.9, 0.9)],
    )

    wr = next(node for node in graph.nodes if node.entity_id == "wr")
    assert wr.projected_impact is None
    assert wr.evidence_path is None
    assert graph.source_impact is None
