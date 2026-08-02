from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)


class EventNormalizer:
    """
    Convert source-neutral ingestion records into Cortex RawEvents.

    The normalizer preserves provider facts and identity metadata but
    does not assign football sentiment, fantasy impact, confidence,
    or recommendations.
    """

    def normalize(
        self,
        record: SourceRecord,
    ) -> RawEvent:
        return RawEvent(
            headline=record.headline,
            source=record.source,
            player=record.player,
            team=record.team,
            position=record.position,
            summary=record.summary,
            published_at=record.published_at,
            url=record.url,
            evidence={
                "source_id": record.source_id,
                "source_metadata": record.metadata,
                "source_count": 1,
                "sources": [record.source],
            },
        )

    def normalize_many(
        self,
        records: list[SourceRecord],
    ) -> list[RawEvent]:
        return [
            self.normalize(record)
            for record in records
        ]
