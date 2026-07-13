from gridiron_cortex.knowledge.knowledge_graph_manager import (
    KnowledgeGraphManager,
)
from gridiron_cortex.models.propagation import (
    PropagationCandidate,
)


class PropagationPlanner:
    """
    Converts knowledge-graph paths into weighted propagation candidates.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphManager,
    ):
        self.knowledge_graph = knowledge_graph

    @staticmethod
    def hop_decay(hops: int) -> float:
        if hops <= 0:
            return 1.0

        if hops == 1:
            return 0.85

        if hops == 2:
            return 0.65

        if hops == 3:
            return 0.40

        return 0.20

    @staticmethod
    def calculate_weight(
        strength: float,
        confidence: float,
        hops: int,
    ) -> float:
        return (
            strength
            * confidence
            * PropagationPlanner.hop_decay(hops)
        )

    def plan(
        self,
        source_entity_id: str,
        max_depth: int = 2,
    ) -> list[PropagationCandidate]:
        if max_depth < 1:
            return []

        graph = self.knowledge_graph.build_graph(
            root_entity_id=source_entity_id,
            max_depth=max_depth,
            direction="outgoing",
        )

        candidates: dict[str, PropagationCandidate] = {}

        for node in graph.nodes:
            if node.entity_id == source_entity_id:
                continue

            paths = self.knowledge_graph.find_paths(
                source_entity_id=source_entity_id,
                target_entity_id=node.entity_id,
                max_depth=max_depth,
            )

            if not paths:
                continue

            best_path = max(
                paths,
                key=lambda path: self.calculate_weight(
                    strength=path.combined_strength,
                    confidence=path.combined_confidence,
                    hops=path.hop_count,
                ),
            )

            weight = self.calculate_weight(
                strength=best_path.combined_strength,
                confidence=best_path.combined_confidence,
                hops=best_path.hop_count,
            )

            candidates[node.entity_id] = PropagationCandidate(
                entity_id=node.entity_id,
                entity_name=node.entity_name,
                entity_type=node.entity_type,
                team=node.team,
                hop_count=best_path.hop_count,
                relationship_strength=best_path.combined_strength,
                relationship_confidence=best_path.combined_confidence,
                propagation_weight=weight,
                reason=self._build_reason(best_path.relationships),
            )

        return sorted(
            candidates.values(),
            key=lambda candidate: candidate.propagation_weight,
            reverse=True,
        )

    @staticmethod
    def _build_reason(relationships) -> str:
        if not relationships:
            return "No relationship path found."

        parts = []

        for relationship in relationships:
            parts.append(
                f"{relationship.source_entity_name} "
                f"--{relationship.relationship_type}--> "
                f"{relationship.target_entity_name}"
            )

        return " | ".join(parts)
