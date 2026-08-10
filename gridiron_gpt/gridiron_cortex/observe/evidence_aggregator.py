from collections import defaultdict

from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.source_evidence import SourceEvidence


class EvidenceAggregator:
    """Groups multiple reports of the same football event."""

    @staticmethod
    def aggregate(
        events: list[CanonicalEvent],
    ) -> list[CanonicalEvent]:

        grouped: dict[str, CanonicalEvent] = {}

        for event in events:
            if event.event_key not in grouped:
                grouped[event.event_key] = event
                continue

            existing = grouped[event.event_key]

            existing.evidence.extend(event.evidence)

            existing.confidence = max(
                existing.confidence,
                event.confidence,
            )

        for event in grouped.values():
            unique_sources = {
                evidence.source
                for evidence in event.evidence
            }

            event.consensus = min(
                len(unique_sources) / 3.0,
                1.0,
            )

        return list(grouped.values())
