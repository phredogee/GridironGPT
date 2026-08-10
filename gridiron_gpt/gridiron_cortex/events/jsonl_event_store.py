from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_types import CortexEventType


class JsonlCortexEventStore:
    """Durable Cortex event store backed by append-only JSONL."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._events: list[CortexEvent] = self._load()
        self._event_ids = {event.event_id for event in self._events}

    def _load(self) -> list[CortexEvent]:
        if not self.path.exists():
            return []
        events: list[CortexEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(CortexEvent.from_dict(json.loads(line)))
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                continue
        return events

    def append(self, event: CortexEvent) -> None:
        if event.event_id in self._event_ids:
            return
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        self._events.append(event)
        self._event_ids.add(event.event_id)

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
            and (correlation_id is None or event.correlation_id == correlation_id)
        )

    def clear(self) -> None:
        self._events.clear()
        self._event_ids.clear()
        if self.path.exists():
            self.path.unlink()
