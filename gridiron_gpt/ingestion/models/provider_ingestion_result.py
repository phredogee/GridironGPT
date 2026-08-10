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
    attempts: int = 1
    error_type: str | None = None
    error_message: str | None = None
    cortex_events_accepted: int = 0
    cortex_duplicates_ignored: int = 0
    processor_failures: int = 0

    @property
    def event_count(self) -> int:
        return len(self.events)
