from abc import ABC, abstractmethod

from gridiron_cortex.models.canonical_event import (
    CanonicalEvent,
)


class CanonicalEventRepository(ABC):
    """
    Persistence contract for canonical football developments.
    """

    @abstractmethod
    def save(
        self,
        canonical_event: CanonicalEvent,
    ) -> None:
        """Persist the current canonical-event snapshot."""
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        event_key: str,
    ) -> CanonicalEvent | None:
        """Return the latest snapshot for an event key."""
        raise NotImplementedError

    @abstractmethod
    def get_history(
        self,
        event_key: str,
    ) -> list[CanonicalEvent]:
        """Return all persisted snapshots for an event key."""
        raise NotImplementedError
