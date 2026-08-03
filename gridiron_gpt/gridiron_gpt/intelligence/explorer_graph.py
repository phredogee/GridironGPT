from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gridiron_cortex.models.entity_relationship import EntityRelationship


@dataclass(frozen=True, slots=True)
class ExplorerGraphNode:
    entity_id: str
    name: str
    team: str | None
    is_root: bool


@dataclass(frozen=True, slots=True)
class ExplorerGraphEdge:
    source_id: str
    target_id: str
    relationship_type: str
    strength: float
    confidence: float


@dataclass(frozen=True, slots=True)
class ExplorerGraph:
    root_id: str
    nodes: tuple[ExplorerGraphNode, ...]
    edges: tuple[ExplorerGraphEdge, ...]


def build_explorer_graph(
    root_id: str,
    relationships: Iterable[EntityRelationship],
    *,
    max_neighbors: int = 10,
) -> ExplorerGraph:
    """Build a one-hop graph around a selected Cortex entity."""
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
        nodes[relationship.source_entity_id] = ExplorerGraphNode(
            entity_id=relationship.source_entity_id,
            name=relationship.source_entity_name,
            team=relationship.source_team,
            is_root=relationship.source_entity_id == root_id,
        )
        nodes[relationship.target_entity_id] = ExplorerGraphNode(
            entity_id=relationship.target_entity_id,
            name=relationship.target_entity_name,
            team=relationship.target_team,
            is_root=relationship.target_entity_id == root_id,
        )
        edges.append(
            ExplorerGraphEdge(
                source_id=relationship.source_entity_id,
                target_id=relationship.target_entity_id,
                relationship_type=relationship.relationship_type,
                strength=float(relationship.strength),
                confidence=float(relationship.confidence),
            )
        )

    return ExplorerGraph(
        root_id=root_id,
        nodes=tuple(nodes.values()),
        edges=tuple(edges),
    )
