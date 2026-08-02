from __future__ import annotations

from dataclasses import dataclass, field

from gridiron_cortex.models.raw_event import RawEvent


@dataclass(frozen=True)
class ProviderIngestionResult:
    """Outcome of one provider execution within the ingestion boundary."""

    source_name: str
    success: bool
    events: list[RawEvent] = field(default_factory=list)
    records_received: int = 0
    error_type: str | None = None
    error_message: str | None = None

    @property
    def event_count(self) -> int:
        return len(self.events)
