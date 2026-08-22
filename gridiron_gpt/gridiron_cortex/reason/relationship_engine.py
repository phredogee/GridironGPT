from gridiron_cortex.models.impact import Impact
from gridiron_cortex.propagation.propagation_planner import (
    PropagationPlanner,
)
from gridiron_cortex.reason.relationship_context import (
    RelationshipContextPolicy,
)
from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantics,
)
from gridiron_cortex.remember.relationship_repository import (
    RelationshipRepository,
)


class RelationshipEngine:
    """
    Creates direct impacts and graph-based propagated impacts.
    """

    def __init__(
        self,
        repository: RelationshipRepository | None = None,
        propagation_planner: PropagationPlanner | None = None,
        relationship_semantics: RelationshipSemantics | None = None,
        relationship_context_policy: RelationshipContextPolicy | None = None,
    ):
        self.repository = repository
        self.propagation_planner = propagation_planner
        self.relationship_semantics = (
            relationship_semantics or RelationshipSemantics()
        )
        self.relationship_context_policy = (
            relationship_context_policy or RelationshipContextPolicy()
        )

    def propagate(self, signal):
        impacts = []
        relationship_context = self.relationship_context_policy.from_signal(signal)

        for entity in signal.entities:
            if entity.entity_type != "player":
                continue

            source_entity_id = self._build_entity_id(entity.name)

            impacts.append(
                Impact(
                    entity_type="player",
                    entity_name=entity.name,
                    team=entity.team,
                    impact_score=signal.impact_score,
                    impact_type="direct",
                    reason="Primary player mentioned in signal.",
                )
            )

            if self.propagation_planner is not None:
                candidates = self.propagation_planner.plan(
                    source_entity_id=source_entity_id,
                    max_depth=2,
                    source_impact_score=signal.impact_score,
                    relationship_context=relationship_context,
                )

                for candidate in candidates:
                    propagated_score = (
                        signal.impact_score
                        * candidate.propagation_weight
                    )

                    if propagated_score == 0:
                        continue

                    impacts.append(
                        Impact(
                            entity_type=candidate.entity_type,
                            entity_name=candidate.entity_name,
                            team=candidate.team,
                            impact_score=propagated_score,
                            impact_type="propagated",
                            reason=candidate.reason,
                            hop_count=candidate.hop_count,
                            relationship_strength=(
                                candidate.relationship_strength
                            ),
                            relationship_confidence=(
                                candidate.relationship_confidence
                            ),
                            propagation_weight=(
                                candidate.propagation_weight
                            ),
                        )
                    )

                continue

            if self.repository is None:
                continue

            relationships = self.repository.get_outgoing(
                source_entity_id
            )

            for relationship in relationships:
                if not relationship_context.allows(
                    relationship.relationship_type
                ):
                    continue

                semantic_multiplier = (
                    self.relationship_semantics.calculate_multiplier(
                        relationship.relationship_type,
                        signal.impact_score,
                    )
                )

                propagated_score = (
                    signal.impact_score
                    * relationship.strength
                    * relationship.confidence
                    * semantic_multiplier
                )

                if propagated_score == 0:
                    continue

                semantic = self.relationship_semantics.get(
                    relationship.relationship_type
                )

                reason = (
                    f"{relationship.relationship_type}: "
                    f"{relationship.reason}"
                )

                if semantic.description:
                    reason = (
                        f"{reason} | "
                        f"{semantic.description}"
                    )

                impacts.append(
                    Impact(
                        entity_type=relationship.target_entity_type,
                        entity_name=relationship.target_entity_name,
                        team=relationship.target_team,
                        impact_score=propagated_score,
                        impact_type="propagated",
                        reason=reason,
                    )
                )

        return impacts

    @staticmethod
    def _build_entity_id(entity_name: str) -> str:
        return entity_name.strip().lower().replace(" ", "_")
