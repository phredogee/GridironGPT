import re

from gridiron_cortex.models.event_classification import (
    EventClassification,
)
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.event_taxonomy import EVENT_RULES


def normalize_event_text(text: str) -> str:
    """
    Normalize event text for deterministic phrase matching.
    """
    normalized = text.casefold()
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


class EventClassifier:
    """
    Deterministic rule-based classifier for football events.
    """

    def classify(self, event: RawEvent) -> EventClassification:
        searchable_text = self._build_searchable_text(event)
        matches: list[EventClassification] = []

        for rule in EVENT_RULES:
            matched_phrases = [
                phrase
                for phrase in rule["phrases"]
                if normalize_event_text(phrase) in searchable_text
            ]

            if not matched_phrases:
                continue

            matches.append(
                EventClassification(
                    category=rule["category"],
                    subtype=rule["subtype"],
                    polarity=rule["polarity"],
                    impact=rule["impact"],
                    confidence=rule["confidence"],
                    matched_rules=matched_phrases,
                    metadata={
                        "classifier": "deterministic_rules",
                    },
                )
            )

        if not matches:
            return EventClassification(
                category="unknown",
                subtype="unclassified",
                polarity="neutral",
                impact=0.0,
                confidence=0.0,
                matched_rules=[],
                metadata={
                    "classifier": "deterministic_rules",
                },
            )

        matches.sort(
            key=lambda classification: (
                classification.confidence,
                max(
                    (
                        len(rule)
                        for rule in classification.matched_rules
                    ),
                    default=0,
                ),
            ),
            reverse=True,
        )

        return matches[0]

    @staticmethod
    def _build_searchable_text(event: RawEvent) -> str:
        evidence_text = " ".join(
            str(value)
            for value in event.evidence.values()
            if value is not None
        )

        combined = " ".join(
            [
                event.headline or "",
                event.summary or "",
                event.event_type or "",
                event.sentiment or "",
                evidence_text,
            ]
        )

        return normalize_event_text(combined)
