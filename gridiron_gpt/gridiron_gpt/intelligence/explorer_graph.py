from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_cortex.models.entity_relationship import EntityRelationship


@dataclass(frozen=True, slots=True)
class ExplorerGraphNode:
    entity_id: str
    name: str
    team: str | None
    is_root: bool
    projected_impact: float | None = None
    propagation_weight: float | None = None
    hop_count: int | None = None
    evidence_path: str | None = None


@dataclass(frozen=True, slots=True)
class ExplorerGraphEdge:
    source_id: str
    target_id: str
    relationship_type: str
    strength: float
    confidence: float
    projected_impact: float | None = None


@dataclass(frozen=True, slots=True)
class ExplorerGraph:
    root_id: str
    nodes: tuple[ExplorerGraphNode, ...]
    edges: tuple[ExplorerGraphEdge, ...]
    source_impact: float | None = None
    seed_headline: str | None = None


def _node_intelligence(
    entity_id: str,
    *,
    impact_by_entity: Mapping[str, float],
    weight_by_entity: Mapping[str, float],
    hops_by_entity: Mapping[str, int],
    path_by_entity: Mapping[str, str],
) -> dict:
    return {
        "projected_impact": impact_by_entity.get(entity_id),
        "propagation_weight": weight_by_entity.get(entity_id),
        "hop_count": hops_by_entity.get(entity_id),
        "evidence_path": path_by_entity.get(entity_id),
    }


def build_explorer_graph(
    root_id: str,
    relationships: Iterable[EntityRelationship],
    *,
    max_neighbors: int = 10,
    impact_by_entity: Mapping[str, float] | None = None,
    weight_by_entity: Mapping[str, float] | None = None,
    hops_by_entity: Mapping[str, int] | None = None,
    path_by_entity: Mapping[str, str] | None = None,
    source_impact: float | None = None,
    seed_headline: str | None = None,
) -> ExplorerGraph:
    """Build a one-hop graph around a selected Cortex entity."""
    impact_by_entity = impact_by_entity or {}
    weight_by_entity = weight_by_entity or {}
    hops_by_entity = hops_by_entity or {}
    path_by_entity = path_by_entity or {}

    connected = [
        relationship
        for relationship in relationships
        if relationship.active
        and (
            relationship.source_entity_id == root_id
            or relationship.target_entity_id == root_id
        )
    ]
    connected.sort(
        key=lambda relationship: -(
            float(relationship.strength) * float(relationship.confidence)
        )
    )
    connected = connected[:max_neighbors]

    nodes: dict[str, ExplorerGraphNode] = {}
    edges: list[ExplorerGraphEdge] = []

    for relationship in connected:
        source_id = relationship.source_entity_id
        target_id = relationship.target_entity_id

        nodes[source_id] = ExplorerGraphNode(
            entity_id=source_id,
            name=relationship.source_entity_name,
            team=relationship.source_team,
            is_root=source_id == root_id,
            **_node_intelligence(
                source_id,
                impact_by_entity=impact_by_entity,
                weight_by_entity=weight_by_entity,
                hops_by_entity=hops_by_entity,
                path_by_entity=path_by_entity,
            ),
        )
        nodes[target_id] = ExplorerGraphNode(
            entity_id=target_id,
            name=relationship.target_entity_name,
            team=relationship.target_team,
            is_root=target_id == root_id,
            **_node_intelligence(
                target_id,
                impact_by_entity=impact_by_entity,
                weight_by_entity=weight_by_entity,
                hops_by_entity=hops_by_entity,
                path_by_entity=path_by_entity,
            ),
        )

        propagated_entity_id = target_id if source_id == root_id else source_id
        edges.append(
            ExplorerGraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship.relationship_type,
                strength=float(relationship.strength),
                confidence=float(relationship.confidence),
                projected_impact=impact_by_entity.get(propagated_entity_id),
            )
        )

    return ExplorerGraph(
        root_id=root_id,
        nodes=tuple(nodes.values()),
        edges=tuple(edges),
        source_impact=source_impact,
        seed_headline=seed_headline,
    )
