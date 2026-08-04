from __future__ import annotations

from collections.abc import Iterable

from gridiron_cortex.activity.activity_formatter import format_activity
from gridiron_cortex.activity.activity_grouping import group_activity
from gridiron_cortex.activity.activity_models import ActivityGroup
from gridiron_cortex.events.event_bus import CortexEventBus
from gridiron_cortex.events.event_types import CortexEventType


class ActivityFeedService:
    def __init__(self, event_bus: CortexEventBus) -> None:
        self.event_bus = event_bus

    def latest(
        self,
        limit: int = 25,
        *,
        event_types: Iterable[CortexEventType] | None = None,
        entity_id: str | None = None,
        entity_name: str | None = None,
    ) -> tuple[ActivityGroup, ...]:
        if limit < 1:
            return ()
        events = self.event_bus.history(
            event_types=event_types,
            entity_id=entity_id,
        )
        if entity_name is not None:
            normalized = entity_name.strip().casefold()
            events = tuple(
                event
                for event in events
                if (event.entity_name or "").strip().casefold() == normalized
            )
        groups = group_activity(format_activity(event) for event in events)
        return groups[:limit]

    def by_player(
        self,
        player_name: str,
        limit: int = 25,
    ) -> tuple[ActivityGroup, ...]:
        return self.latest(limit=limit, entity_name=player_name)

    def by_type(
        self,
        event_type: CortexEventType,
        limit: int = 25,
    ) -> tuple[ActivityGroup, ...]:
        return self.latest(limit=limit, event_types=(event_type,))

    def by_correlation(self, correlation_id: str) -> ActivityGroup | None:
        events = self.event_bus.history(correlation_id=correlation_id)
        groups = group_activity(format_activity(event) for event in events)
        return groups[0] if groups else None
