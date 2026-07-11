from collections import deque

from gridiron_cortex.knowledge.knowledge_service import KnowledgeService
from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.models.knowledge_graph import (
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    RelationshipPath,
)


class KnowledgeGraphManager:
    """
    Query and traversal layer for persistent entity relationships.

    The manager does not own storage. It queries relationship knowledge
    through KnowledgeService and converts it into graph structures.
    """

    def __init__(self, knowledge_service: KnowledgeService):
        self.knowledge = knowledge_service

    def get_neighbors(
        self,
        entity_id: str,
        direction: str = "both",
    ) -> list[EntityRelationship]:
        """
        Return immediate active relationships for an entity.

        direction:
            outgoing - relationships originating from the entity
            incoming - relationships pointing to the entity
            both     - incoming and outgoing relationships
        """
        normalized_direction = direction.strip().lower()

        if normalized_direction == "outgoing":
            return self.knowledge.get_outgoing_relationships(entity_id)

        if normalized_direction == "incoming":
            return self.knowledge.get_incoming_relationships(entity_id)

        if normalized_direction == "both":
            return self._deduplicate_relationships(
                self.knowledge.get_outgoing_relationships(entity_id)
                + self.knowledge.get_incoming_relationships(entity_id)
            )

        raise ValueError(
            "direction must be 'outgoing', 'incoming', or 'both'"
        )

    def build_graph(
        self,
        root_entity_id: str,
        max_depth: int = 2,
        direction: str = "outgoing",
    ) -> KnowledgeGraph:
        """
        Build a cycle-safe graph starting from one entity.

        max_depth=1 returns immediate neighbors.
        max_depth=2 includes neighbors of neighbors.
        """
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative")

        graph = KnowledgeGraph(root_entity_id=root_entity_id)

        visited_depth: dict[str, int] = {root_entity_id: 0}
        queue = deque([(root_entity_id, 0)])

        nodes: dict[str, GraphNode] = {}
        edges: dict[tuple[str, str, str], GraphEdge] = {}

        while queue:
            current_entity_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            relationships = self.get_neighbors(
                current_entity_id,
                direction=direction,
            )

            for relationship in relationships:
                self._add_relationship_nodes(nodes, relationship)
                self._add_relationship_edge(edges, relationship)

                neighbor_id = self._get_neighbor_id(
                    current_entity_id,
                    relationship,
                )

                next_depth = depth + 1
                prior_depth = visited_depth.get(neighbor_id)

                if prior_depth is None or next_depth < prior_depth:
                    visited_depth[neighbor_id] = next_depth
                    queue.append((neighbor_id, next_depth))

        graph.nodes = list(nodes.values())
        graph.edges = list(edges.values())

        return graph

    def find_paths(
        self,
        source_entity_id: str,
        target_entity_id: str,
        max_depth: int = 3,
    ) -> list[RelationshipPath]:
        """
        Find cycle-safe outgoing relationship paths between two entities.
        """
        if max_depth < 1:
            return []

        paths: list[RelationshipPath] = []

        queue = deque(
            [
                (
                    source_entity_id,
                    [],
                    {source_entity_id},
                )
            ]
        )

        while queue:
            current_entity_id, current_path, visited = queue.popleft()

            if len(current_path) >= max_depth:
                continue

            relationships = self.knowledge.get_outgoing_relationships(
                current_entity_id
            )

            for relationship in relationships:
                next_entity_id = relationship.target_entity_id

                if next_entity_id in visited:
                    continue

                new_path = current_path + [relationship]

                if next_entity_id == target_entity_id:
                    paths.append(
                        RelationshipPath(
                            source_entity_id=source_entity_id,
                            target_entity_id=target_entity_id,
                            relationships=new_path,
                        )
                    )
                    continue

                queue.append(
                    (
                        next_entity_id,
                        new_path,
                        visited | {next_entity_id},
                    )
                )

        return paths

    def get_affected_entities(
        self,
        source_entity_id: str,
        max_depth: int = 2,
    ) -> list[GraphNode]:
        """
        Return entities reachable from the source through outgoing edges.
        """
        graph = self.build_graph(
            root_entity_id=source_entity_id,
            max_depth=max_depth,
            direction="outgoing",
        )

        return [
            node
            for node in graph.nodes
            if node.entity_id != source_entity_id
        ]

    @staticmethod
    def _get_neighbor_id(
        current_entity_id: str,
        relationship: EntityRelationship,
    ) -> str:
        if relationship.source_entity_id == current_entity_id:
            return relationship.target_entity_id

        return relationship.source_entity_id

    @staticmethod
    def _add_relationship_nodes(
        nodes: dict[str, GraphNode],
        relationship: EntityRelationship,
    ) -> None:
        nodes.setdefault(
            relationship.source_entity_id,
            GraphNode(
                entity_id=relationship.source_entity_id,
                entity_name=relationship.source_entity_name,
                entity_type=relationship.source_entity_type,
                team=relationship.source_team,
            ),
        )

        nodes.setdefault(
            relationship.target_entity_id,
            GraphNode(
                entity_id=relationship.target_entity_id,
                entity_name=relationship.target_entity_name,
                entity_type=relationship.target_entity_type,
                team=relationship.target_team,
            ),
        )

    @staticmethod
    def _add_relationship_edge(
        edges: dict[tuple[str, str, str], GraphEdge],
        relationship: EntityRelationship,
    ) -> None:
        key = (
            relationship.source_entity_id,
            relationship.target_entity_id,
            relationship.relationship_type,
        )

        edges[key] = GraphEdge(
            source_entity_id=relationship.source_entity_id,
            target_entity_id=relationship.target_entity_id,
            relationship_type=relationship.relationship_type,
            strength=relationship.strength,
            confidence=relationship.confidence,
            active=relationship.active,
            reason=relationship.reason,
        )

    @staticmethod
    def _deduplicate_relationships(
        relationships: list[EntityRelationship],
    ) -> list[EntityRelationship]:
        unique: dict[
            tuple[str, str, str],
            EntityRelationship,
        ] = {}

        for relationship in relationships:
            key = (
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type,
            )
            unique[key] = relationship

        return list(unique.values())

