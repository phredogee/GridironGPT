from gridiron_cortex.models.impact import Impact
from gridiron_cortex.storage.relationship_repository import (
    RelationshipRepository,
)


class RelationshipEngine:
    """
    Creates direct impacts and propagates signals through stored relationships.
    """

    def __init__(
        self,
        repository: RelationshipRepository | None = None,
    ):
        self.repository = repository

    def propagate(self, signal):
        impacts = []

        for entity in signal.entities:
            if entity.entity_type != "player":
                continue

            source_player_id = self._build_entity_id(entity.name)

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

            if self.repository is None:
                continue

            relationships = self.repository.get_outgoing(
                source_player_id
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
