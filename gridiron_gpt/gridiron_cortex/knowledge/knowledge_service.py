from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.storage.event_repository import EventRepository
from gridiron_cortex.storage.player_scorecard_repository import (
    PlayerScorecardRepository,
)
from gridiron_cortex.storage.relationship_repository import (
    RelationshipRepository,
)


class KnowledgeService:
    """
    Central access layer for persistent Cortex knowledge.

    The service hides repository implementations from the engine,
    facade, and applications.
    """

    def __init__(
        self,
        event_repository: EventRepository,
        player_scorecard_repository: PlayerScorecardRepository,
        relationship_repository: RelationshipRepository,
    ):
        self.event_repository = event_repository
        self.player_scorecard_repository = player_scorecard_repository
        self.relationship_repository = relationship_repository

    # Events

    def has_event(self, event: RawEvent) -> bool:
        return self.event_repository.contains(event.fingerprint())

    def save_event(self, event: RawEvent) -> None:
        self.event_repository.save(event)

    # Player scorecards

    def get_latest_scorecard(
        self,
        player_id: str,
    ) -> PlayerScorecard | None:
        return self.player_scorecard_repository.get_latest(player_id)

    def get_scorecard_history(
        self,
        player_id: str,
    ) -> list[PlayerScorecard]:
        return self.player_scorecard_repository.get_history(player_id)

    def save_scorecard(
        self,
        scorecard: PlayerScorecard,
    ) -> None:
        self.player_scorecard_repository.save(scorecard)

    # Relationships

    def save_relationship(
        self,
        relationship: EntityRelationship,
    ) -> None:
        self.relationship_repository.save(relationship)

    def get_outgoing_relationships(
        self,
        entity_id: str,
    ) -> list[EntityRelationship]:
        return self.relationship_repository.get_outgoing(entity_id)

    def get_incoming_relationships(
        self,
        entity_id: str,
    ) -> list[EntityRelationship]:
        return self.relationship_repository.get_incoming(entity_id)

    def get_relationship_history(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str | None = None,
    ) -> list[EntityRelationship]:
        return self.relationship_repository.get_between(
            source_entity_id,
            target_entity_id,
            relationship_type,
        )
