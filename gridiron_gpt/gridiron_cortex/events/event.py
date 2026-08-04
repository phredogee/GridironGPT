from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from gridiron_cortex.events.event_types import CortexEventType


@dataclass(frozen=True, slots=True)
class CortexEvent:
    event_type: CortexEventType
    entity_id: str | None = None
    entity_name: str | None = None
    source: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    engine_version: str = "cortex-dev"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "source": self.source,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "engine_version": self.engine_version,
        }

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "CortexEvent":
        timestamp = datetime.fromisoformat(str(record["timestamp"]))
        return cls(
            event_id=str(record["event_id"]),
            timestamp=timestamp,
            event_type=CortexEventType(str(record["event_type"])),
            entity_id=record.get("entity_id"),
            entity_name=record.get("entity_name"),
            source=record.get("source"),
            payload=record.get("payload") or {},
            correlation_id=str(record["correlation_id"]),
            engine_version=str(record.get("engine_version", "cortex-dev")),
        )
