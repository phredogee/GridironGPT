from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.models.provider_ingestion_result import (
    ProviderIngestionResult,
)
from gridiron_gpt.ingestion.normalize.event_normalizer import (
    EventNormalizer,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class IngestionService:
    """
    Coordinate source retrieval and event normalization.

    Provider execution is isolated so one failing source does not prevent
    healthy providers from producing normalized RawEvents.
    """

    def __init__(
        self,
        normalizer: EventNormalizer | None = None,
    ):
        self.normalizer = normalizer or EventNormalizer()

    def ingest_result(
        self,
        adapter: SourceAdapter,
    ) -> ProviderIngestionResult:
        source_name = adapter.source_name

        try:
            records = adapter.fetch()
            events = self.normalizer.normalize_many(records)
        except Exception as exc:
            return ProviderIngestionResult(
                source_name=source_name,
                success=False,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

        return ProviderIngestionResult(
            source_name=source_name,
            success=True,
            events=events,
            records_received=len(records),
        )

    def ingest(
        self,
        adapter: SourceAdapter,
    ) -> list[RawEvent]:
        """Compatibility API returning only normalized events."""
        return self.ingest_result(adapter).events

    def ingest_many_results(
        self,
        adapters: list[SourceAdapter],
    ) -> list[ProviderIngestionResult]:
        return [
            self.ingest_result(adapter)
            for adapter in adapters
        ]

    def ingest_many(
        self,
        adapters: list[SourceAdapter],
    ) -> list[RawEvent]:
        """Compatibility API that returns events from successful providers."""
        events: list[RawEvent] = []

        for result in self.ingest_many_results(adapters):
            events.extend(result.events)

        return events
