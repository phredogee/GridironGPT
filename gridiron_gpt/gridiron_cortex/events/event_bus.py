from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_store import InMemoryEventStore
from gridiron_cortex.events.event_types import CortexEventType

EventHandler = Callable[[CortexEvent], None]


class CortexEventBus:
    def __init__(
        self,
        store: InMemoryEventStore | None = None,
    ) -> None:
        self.store = store or InMemoryEventStore()
        self._subscribers: dict[
            CortexEventType | None,
            list[EventHandler],
        ] = defaultdict(list)

    def subscribe(
        self,
        handler: EventHandler,
        event_type: CortexEventType | None = None,
    ) -> Callable[[], None]:
        self._subscribers[event_type].append(handler)

        def unsubscribe() -> None:
            handlers = self._subscribers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

        return unsubscribe

    def publish(self, event: CortexEvent) -> CortexEvent:
        self.store.append(event)
        handlers = (
            tuple(self._subscribers.get(None, ()))
            + tuple(self._subscribers.get(event.event_type, ()))
        )
        for handler in handlers:
            handler(event)
        return event

    def publish_many(
        self,
        events: Iterable[CortexEvent],
    ) -> tuple[CortexEvent, ...]:
        return tuple(self.publish(event) for event in events)

    def replay(
        self,
        handler: EventHandler,
        *,
        event_types: Iterable[CortexEventType] | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
    ) -> int:
        events = self.store.filter(
            event_types=event_types,
            entity_id=entity_id,
            correlation_id=correlation_id,
        )
        for event in events:
            handler(event)
        return len(events)

    def latest(self, limit: int = 20) -> tuple[CortexEvent, ...]:
        return self.store.latest(limit)

    def history(
        self,
        *,
        event_types: Iterable[CortexEventType] | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[CortexEvent, ...]:
        return self.store.filter(
            event_types=event_types,
            entity_id=entity_id,
            correlation_id=correlation_id,
        )
