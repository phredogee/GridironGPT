import re
from hashlib import sha256

from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.understand.event_classifier import EventClassifier


class EvidenceAggregator:
    """
    Group reports that describe the same football development.
    """

    def __init__(self):
        self.classifier = EventClassifier()
        self._events: dict[str, CanonicalEvent] = {}

    def add(self, event: RawEvent) -> CanonicalEvent:
        classification = self.classifier.classify(event)

        event_key = self._build_event_key(
            event=event,
            category=classification.category,
            subtype=classification.subtype,
        )

        source_evidence = SourceEvidence(
            headline=event.headline,
            source=event.source,
            published_at=event.published_at,
            url=event.url,
            confidence=classification.confidence,
            metadata={
                "raw_event_fingerprint": event.fingerprint(),
            },
        )

        canonical_event = self._events.get(event_key)

        if canonical_event is None:
            canonical_event = CanonicalEvent(
                event_key=event_key,
                player=event.player,
                team=event.team,
                category=classification.category,
                subtype=classification.subtype,
                polarity=classification.polarity,
                impact=classification.impact,
                confidence=classification.confidence,
                evidence=[source_evidence],
            )

            self._events[event_key] = canonical_event
            return canonical_event

        if not self._already_contains(
            canonical_event,
            event.fingerprint(),
        ):
            canonical_event.evidence.append(source_evidence)

        canonical_event.confidence = self._aggregate_confidence(
            canonical_event
        )

        return canonical_event

    @staticmethod
    def _build_event_key(
        event: RawEvent,
        category: str,
        subtype: str,
    ) -> str:
        player = EvidenceAggregator._normalize(event.player)
        team = EvidenceAggregator._normalize(event.team)

        payload = "|".join(
            [
                player,
                team,
                category,
                subtype,
            ]
        )

        return sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize(value: str | None) -> str:
        if not value:
            return ""

        normalized = value.strip().casefold()
        return re.sub(r"\s+", " ", normalized)

    @staticmethod
    def _already_contains(
        canonical_event: CanonicalEvent,
        fingerprint: str,
    ) -> bool:
        return any(
            evidence.metadata.get("raw_event_fingerprint")
            == fingerprint
            for evidence in canonical_event.evidence
        )

    @staticmethod
    def _aggregate_confidence(
        canonical_event: CanonicalEvent,
    ) -> float:
        """
        Increase confidence as independent sources corroborate an event.
        """

        source_count = len(canonical_event.sources)

        boosts = {
            1: 0.00,
            2: 0.03,
            3: 0.05,
            4: 0.06,
            5: 0.07,
        }
        confidence_boost = boosts.get(source_count, 0.08)

        return min(
            canonical_event.confidence + confidence_boost,
            1.0,
        )
