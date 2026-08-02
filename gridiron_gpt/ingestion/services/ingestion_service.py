from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.normalize.event_normalizer import (
    EventNormalizer,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class IngestionService:
    """
    Coordinate source retrieval and event normalization.

    The service converts external source evidence into normalized
    RawEvents without performing Cortex interpretation.
    """

    def __init__(
        self,
        normalizer: EventNormalizer | None = None,
    ):
        self.normalizer = normalizer or EventNormalizer()

    def ingest(
        self,
        adapter: SourceAdapter,
    ) -> list[RawEvent]:
        records = adapter.fetch()

        return self.normalizer.normalize_many(records)

    def ingest_many(
        self,
        adapters: list[SourceAdapter],
    ) -> list[RawEvent]:
        events: list[RawEvent] = []

        for adapter in adapters:
            events.extend(
                self.ingest(adapter)
            )

        return events
