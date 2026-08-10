from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_cortex.models.entity_relationship import EntityRelationship


@dataclass(frozen=True, slots=True)
class ExplorerGraphNode:
    entity_id: str
    name: str
    team: str | None
    is_root: bool
    depth: int = 0
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
    max_depth: int = 1


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


def _impact_matches(
    entity_id: str,
    impact_by_entity: Mapping[str, float],
    impact_direction: str,
) -> bool:
    if impact_direction == "all":
        return True

    impact = impact_by_entity.get(entity_id)
    if impact_direction == "affected":
        return impact is not None and impact != 0
    if impact_direction == "positive":
        return impact is not None and impact > 0
    if impact_direction == "negative":
        return impact is not None and impact < 0

    raise ValueError(
        "impact_direction must be all, affected, positive, or negative"
    )


def build_explorer_graph(
    root_id: str,
    relationships: Iterable[EntityRelationship],
    *,
    max_neighbors: int = 18,
    max_depth: int = 1,
    relationship_types: set[str] | None = None,
    impact_direction: str = "all",
    impact_by_entity: Mapping[str, float] | None = None,
    weight_by_entity: Mapping[str, float] | None = None,
    hops_by_entity: Mapping[str, int] | None = None,
    path_by_entity: Mapping[str, str] | None = None,
    source_impact: float | None = None,
    seed_headline: str | None = None,
) -> ExplorerGraph:
    """Build a filtered, cycle-safe multi-hop graph around an entity."""
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")
    if max_neighbors < 1:
        raise ValueError("max_neighbors must be at least 1")

    impact_by_entity = impact_by_entity or {}
    weight_by_entity = weight_by_entity or {}
    hops_by_entity = hops_by_entity or {}
    path_by_entity = path_by_entity or {}

    active = [
        relationship
        for relationship in relationships
        if relationship.active
        and (
            not relationship_types
            or relationship.relationship_type in relationship_types
        )
    ]

    adjacency: dict[str, list[EntityRelationship]] = defaultdict(list)
    for relationship in active:
        adjacency[relationship.source_entity_id].append(relationship)
        adjacency[relationship.target_entity_id].append(relationship)

    for rows in adjacency.values():
        rows.sort(
            key=lambda relationship: -(
                float(relationship.strength)
                * float(relationship.confidence)
            )
        )

    discovered_depth: dict[str, int] = {root_id: 0}
    selected_relationships: dict[
        tuple[str, str, str], EntityRelationship
    ] = {}
    queue = deque([root_id])

    while queue and len(discovered_depth) - 1 < max_neighbors:
        current_id = queue.popleft()
        current_depth = discovered_depth[current_id]
        if current_depth >= max_depth:
            continue

        for relationship in adjacency.get(current_id, []):
            neighbor_id = (
                relationship.target_entity_id
                if relationship.source_entity_id == current_id
                else relationship.source_entity_id
            )
            if neighbor_id != root_id and not _impact_matches(
                neighbor_id,
                impact_by_entity,
                impact_direction,
            ):
                continue

            next_depth = current_depth + 1
            prior_depth = discovered_depth.get(neighbor_id)
            if prior_depth is None:
                if len(discovered_depth) - 1 >= max_neighbors:
                    break
                discovered_depth[neighbor_id] = next_depth
                queue.append(neighbor_id)
            elif next_depth < prior_depth:
                discovered_depth[neighbor_id] = next_depth

            key = (
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type,
            )
            selected_relationships[key] = relationship

    nodes: dict[str, ExplorerGraphNode] = {}
    edges: list[ExplorerGraphEdge] = []

    for relationship in selected_relationships.values():
        source_id = relationship.source_entity_id
        target_id = relationship.target_entity_id
        if source_id not in discovered_depth or target_id not in discovered_depth:
            continue

        nodes[source_id] = ExplorerGraphNode(
            entity_id=source_id,
            name=relationship.source_entity_name,
            team=relationship.source_team,
            is_root=source_id == root_id,
            depth=discovered_depth[source_id],
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
            depth=discovered_depth[target_id],
            **_node_intelligence(
                target_id,
                impact_by_entity=impact_by_entity,
                weight_by_entity=weight_by_entity,
                hops_by_entity=hops_by_entity,
                path_by_entity=path_by_entity,
            ),
        )

        propagated_entity_id = (
            target_id
            if discovered_depth[target_id] >= discovered_depth[source_id]
            else source_id
        )
        edges.append(
            ExplorerGraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship.relationship_type,
                strength=float(relationship.strength),
                confidence=float(relationship.confidence),
                projected_impact=impact_by_entity.get(
                    propagated_entity_id
                ),
            )
        )

    return ExplorerGraph(
        root_id=root_id,
        nodes=tuple(
            sorted(nodes.values(), key=lambda node: (node.depth, node.name))
        ),
        edges=tuple(edges),
        source_impact=source_impact,
        seed_headline=seed_headline,
        max_depth=max_depth,
    )
