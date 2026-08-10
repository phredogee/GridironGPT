from abc import ABC, abstractmethod

from gridiron_cortex.models.entity_relationship import EntityRelationship


class RelationshipRepository(ABC):
    """
    Persistence contract for entity relationships.
    """

    @abstractmethod
    def save(self, relationship: EntityRelationship) -> None:
        """Persist a relationship snapshot."""
        raise NotImplementedError

    @abstractmethod
    def get_outgoing(
        self,
        source_entity_id: str,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        """Return relationships originating from an entity."""
        raise NotImplementedError

    @abstractmethod
    def get_incoming(
        self,
        target_entity_id: str,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        """Return relationships pointing to an entity."""
        raise NotImplementedError

    @abstractmethod
    def get_current(
        self,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        """Return the latest snapshot of every relationship."""
        raise NotImplementedError

    @abstractmethod
    def get_between(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str | None = None,
    ) -> list[EntityRelationship]:
        """Return relationship history between two entities."""
        raise NotImplementedError
