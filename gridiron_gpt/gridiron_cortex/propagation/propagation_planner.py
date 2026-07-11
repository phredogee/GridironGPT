from collections import deque

from gridiron_cortex.knowledge.knowledge_graph_manager import (
    KnowledgeGraphManager,
)
from gridiron_cortex.models.propagation import (
    PropagationCandidate,
)


class PropagationPlanner:

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
        if not source_entity_id:
            raise ValueError("source_entity_id cannot be empty")

        if max_depth < 1:
            return []

        candidates: dict[str, PropagationCandidate] = {}

        queue = deque(
            [
                (
                    source_entity_id,
                    0,
                    1.0,
                    1.0,
                    [],
                    {source_entity_id},
                )
            ]
        )

        while queue:
            (
                current_entity_id,
                current_hops,
                cumulative_strength,
                cumulative_confidence,
                relationship_reasons,
                visited,
            ) = queue.popleft()

            if current_hops >= max_depth:
                continue

            relationships = self.knowledge_graph.get_neighbors(
                current_entity_id,
                direction="outgoing",
            )

            for relationship in relationships:
                target_entity_id = relationship.target_entity_id

                if target_entity_id in visited:
                    continue

                hop_count = current_hops + 1

                path_strength = (
                    cumulative_strength
                    * relationship.strength
                )

                path_confidence = (
                    cumulative_confidence
                    * relationship.confidence
                )

                weight = self.calculate_weight(
                    strength=path_strength,
                    confidence=path_confidence,
                    hops=hop_count,
                )

                reason_parts = relationship_reasons + [
                    (
                        f"{relationship.relationship_type}: "
                        f"{relationship.reason}"
                    )
                ]

                candidate = PropagationCandidate(
                    entity_id=target_entity_id,
                    entity_name=relationship.target_entity_name,
                    entity_type=relationship.target_entity_type,
                    team=relationship.target_team,
                    hop_count=hop_count,
                    relationship_strength=path_strength,
                    relationship_confidence=path_confidence,
                    propagation_weight=weight,
                    reason=" -> ".join(reason_parts),
                )

                existing = candidates.get(target_entity_id)

                if (
                    existing is None
                    or candidate.propagation_weight
                    > existing.propagation_weight
                ):
                    candidates[target_entity_id] = candidate

                queue.append(
                    (
                        target_entity_id,
                        hop_count,
                        path_strength,
                        path_confidence,
                        reason_parts,
                        visited | {target_entity_id},
                    )
                )

        return sorted(
            candidates.values(),
            key=lambda candidate: (
                candidate.hop_count,
                -candidate.propagation_weight,
                candidate.entity_name,
            ),
        )
