from gridiron_cortex.models.impact import Impact
from gridiron_cortex.propagation.propagation_planner import (
    PropagationPlanner,
)
from gridiron_cortex.storage.relationship_repository import (
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
    ):
        self.repository = repository
        self.propagation_planner = propagation_planner

    def propagate(self, signal):
        impacts = []

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
                        )
                    )

                continue

            if self.repository is None:
                continue

            relationships = self.repository.get_outgoing(
                source_entity_id
            )

            for relationship in relationships:
                propagated_score = (
                    signal.impact_score
                    * relationship.strength
                    * relationship.confidence
                )

                if propagated_score == 0:
                    continue

                impacts.append(
                    Impact(
                        entity_type=relationship.target_entity_type,
                        entity_name=relationship.target_entity_name,
                        team=relationship.target_team,
                        impact_score=propagated_score,
                        impact_type="propagated",
                        reason=(
                            f"{relationship.relationship_type}: "
                            f"{relationship.reason}"
                        ),
                    )
                )

        return impacts

    @staticmethod
    def _build_entity_id(entity_name: str) -> str:
        return entity_name.strip().lower().replace(" ", "_")
