from abc import ABC, abstractmethod

from gridiron_cortex.models.raw_event import RawEvent


class EventRepository(ABC):
    """
    Persistence contract for normalized events.
    """

    @abstractmethod
    def contains(self, fingerprint: str) -> bool:
        """Return whether an event has already been stored."""
        raise NotImplementedError

    @abstractmethod
    def save(self, event: RawEvent) -> None:
        """Persist a new event."""
        raise NotImplementedError
