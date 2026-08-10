from gridiron_cortex.knowledge.knowledge_graph_manager import (
    KnowledgeGraphManager,
)
from gridiron_cortex.models.propagation import PropagationCandidate
from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantics,
)


class PropagationPlanner:
    """Convert knowledge-graph paths into semantic propagation candidates."""

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphManager,
        relationship_semantics: RelationshipSemantics | None = None,
    ):
        self.knowledge_graph = knowledge_graph
        self.relationship_semantics = (
            relationship_semantics or RelationshipSemantics()
        )

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
        semantic_multiplier: float = 1.0,
    ) -> float:
        return (
            strength
            * confidence
            * semantic_multiplier
            * PropagationPlanner.hop_decay(hops)
        )

    def calculate_path_semantic_multiplier(
        self,
        relationships,
        source_impact_score: float,
    ) -> float:
        """Calculate combined semantics across an ordered graph path.

        The running score is updated after every edge. This matters for
        inverse relationships: once a signal changes direction, subsequent
        edges evaluate the new direction rather than the original direction.
        """

        if source_impact_score == 0:
            return 0.0

        running_score = source_impact_score

        for relationship in relationships:
            multiplier = (
                self.relationship_semantics.calculate_multiplier(
                    relationship.relationship_type,
                    running_score,
                )
            )

            running_score *= multiplier

            if running_score == 0:
                return 0.0

        return running_score / source_impact_score

    def plan(
        self,
        source_entity_id: str,
        max_depth: int = 2,
        source_impact_score: float = 1.0,
    ) -> list[PropagationCandidate]:
        if max_depth < 1 or source_impact_score == 0:
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

            def path_weight(path) -> float:
                semantic_multiplier = (
                    self.calculate_path_semantic_multiplier(
                        relationships=path.relationships,
                        source_impact_score=source_impact_score,
                    )
                )

                return self.calculate_weight(
                    strength=path.combined_strength,
                    confidence=path.combined_confidence,
                    hops=path.hop_count,
                    semantic_multiplier=semantic_multiplier,
                )

            # Select the path with the largest absolute effect. A strongly
            # negative path is as important as a strongly positive one.
            best_path = max(
                paths,
                key=lambda path: abs(path_weight(path)),
            )

            semantic_multiplier = (
                self.calculate_path_semantic_multiplier(
                    relationships=best_path.relationships,
                    source_impact_score=source_impact_score,
                )
            )

            weight = self.calculate_weight(
                strength=best_path.combined_strength,
                confidence=best_path.combined_confidence,
                hops=best_path.hop_count,
                semantic_multiplier=semantic_multiplier,
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
                reason=self._build_reason(
                    best_path.relationships,
                    source_impact_score,
                ),
            )

        return sorted(
            candidates.values(),
            key=lambda candidate: abs(
                candidate.propagation_weight
            ),
            reverse=True,
        )

    def _build_reason(
        self,
        relationships,
        source_impact_score: float,
    ) -> str:
        if not relationships:
            return "No relationship path found."

        parts = []
        running_score = source_impact_score

        for relationship in relationships:
            semantic = self.relationship_semantics.get(
                relationship.relationship_type
            )
            multiplier = semantic.multiplier_for(running_score)

            parts.append(
                f"{relationship.source_entity_name} "
                f"--{relationship.relationship_type}"
                f"({multiplier:+.2f})--> "
                f"{relationship.target_entity_name}"
            )

            running_score *= multiplier

        return " | ".join(parts)
