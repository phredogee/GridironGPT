from __future__ import annotations

from collections.abc import Iterable

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_types import CortexEventType


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: list[CortexEvent] = []

    def append(self, event: CortexEvent) -> None:
        self._events.append(event)

    def all(self) -> tuple[CortexEvent, ...]:
        return tuple(self._events)

    def latest(self, limit: int = 20) -> tuple[CortexEvent, ...]:
        if limit < 0:
            raise ValueError("limit cannot be negative")
        if limit == 0:
            return ()
        return tuple(self._events[-limit:])

    def filter(
        self,
        *,
        event_types: Iterable[CortexEventType] | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[CortexEvent, ...]:
        selected_types = set(event_types or ())
        return tuple(
            event
            for event in self._events
            if (not selected_types or event.event_type in selected_types)
            and (entity_id is None or event.entity_id == entity_id)
            and (
                correlation_id is None
                or event.correlation_id == correlation_id
            )
        )

    def clear(self) -> None:
        self._events.clear()
