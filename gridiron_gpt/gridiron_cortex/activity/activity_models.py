from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from gridiron_cortex.events.event_types import CortexEventType


class ActivitySeverity(StrEnum):
    INFO = "info"
    POSITIVE = "positive"
    WARNING = "warning"
    NEGATIVE = "negative"


@dataclass(frozen=True, slots=True)
class ActivityCard:
    event_id: str
    timestamp: datetime
    event_type: CortexEventType
    icon: str
    title: str
    subtitle: str
    severity: ActivitySeverity
    correlation_id: str
    entity_id: str | None = None
    entity_name: str | None = None
    source: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))


@dataclass(frozen=True, slots=True)
class ActivityGroup:
    correlation_id: str
    headline: str
    timestamp: datetime
    cards: tuple[ActivityCard, ...]
    source: str | None = None
    entity_name: str | None = None

    @property
    def latest_timestamp(self) -> datetime:
        return max(card.timestamp for card in self.cards)

    @property
    def event_count(self) -> int:
        return len(self.cards)
