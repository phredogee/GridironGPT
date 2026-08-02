import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256

from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.remember.canonical_event_repository import (
    CanonicalEventRepository,
)
from gridiron_cortex.understand.event_classifier import EventClassifier
from gridiron_cortex.understand.source_reliability import (
    SourceReliability,
)


class _InMemoryCanonicalEventRepository(CanonicalEventRepository):
    """Default process-local repository used when persistence is not injected."""

    def __init__(self):
        self._events: dict[str, CanonicalEvent] = {}
        self._history: dict[str, list[CanonicalEvent]] = {}

    def save(self, canonical_event: CanonicalEvent) -> None:
        self._events[canonical_event.event_key] = canonical_event
        self._history.setdefault(canonical_event.event_key, []).append(
            canonical_event
        )

    def get(self, event_key: str) -> CanonicalEvent | None:
        return self._events.get(event_key)

    def get_history(self, event_key: str) -> list[CanonicalEvent]:
        return list(self._history.get(event_key, []))


class EvidenceAggregator:
    """
    Group reports that describe the same football development.

    Canonical state is read from and written through a
    CanonicalEventRepository. A process-local repository is used by default
    so existing callers keep their current behavior, while persistent
    repositories can be injected for state that survives process restarts.
    """

    def __init__(
        self,
        repository: CanonicalEventRepository | None = None,
    ):
        self.classifier = EventClassifier()
        self.reliability = SourceReliability()
        self.repository = repository or _InMemoryCanonicalEventRepository()

    def add(self, event: RawEvent) -> CanonicalEvent:
        classification = self.classifier.classify(event)

        event_key = self._build_event_key(
            event=event,
            category=classification.category,
            subtype=classification.subtype,
        )

        fingerprint = event.fingerprint()

        source_evidence = SourceEvidence(
            headline=event.headline,
            source=event.source,
            category=classification.category,
            subtype=classification.subtype,
            published_at=event.published_at,
            url=event.url,
            confidence=classification.confidence,
            metadata={
                "raw_event_fingerprint": fingerprint,
            },
        )

        canonical_event = self.repository.get(event_key)

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

            self.repository.save(canonical_event)
            return canonical_event

        if self._already_contains(
            canonical_event,
            fingerprint,
        ):
            return canonical_event

        canonical_event.evidence.append(source_evidence)
        canonical_event.confidence = self._aggregate_confidence(
            canonical_event
        )
        self.repository.save(canonical_event)

        return canonical_event

    @staticmethod
    def _build_event_key(
        event: RawEvent,
        category: str,
        subtype: str,
    ) -> str:
        player = EvidenceAggregator._normalize(event.player)
        team = EvidenceAggregator._normalize(event.team)
        event_date = EvidenceAggregator._event_date(event.published_at)

        payload = "|".join(
            [
                player,
                team,
                category,
                subtype,
                event_date,
            ]
        )

        return sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _event_date(published_at: str | None) -> str:
        """Return a stable calendar-day bucket for canonical identity."""
        if not published_at:
            return ""

        value = published_at.strip()

        try:
            return parsedate_to_datetime(value).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            pass

        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).date().isoformat()
        except ValueError:
            return ""

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

    def _aggregate_confidence(
        self,
        canonical_event: CanonicalEvent,
    ) -> float:
        """
        Increase confidence as independent sources corroborate an event.
        """
        confidence_boost = self.reliability.confidence_boost(
            canonical_event.sources
        )

        return min(
            canonical_event.confidence + confidence_boost,
            1.0,
        )
