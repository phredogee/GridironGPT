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

    ``classify`` preserves the original single-best-match contract used by
    existing Cortex callers. ``classify_all`` exposes every distinct signal
    found in the event so richer consumers can reason over compound news.
    """

    GENERIC_ABSENCE_PHRASES = {
        "will not play",
        "won't play",
    }

    INJURY_CONTEXT_PHRASES = {
        "injury",
        "injured",
        "hamstring",
        "ankle",
        "knee",
        "shoulder",
        "concussion",
        "achilles",
        "calf",
        "groin",
        "foot",
        "back injury",
        "illness",
    }

    def classify(self, event: RawEvent) -> EventClassification:
        matches = self.classify_all(event)

        if not matches:
            return self._unknown_classification()

        return matches[0]

    def classify_all(self, event: RawEvent) -> list[EventClassification]:
        """
        Return all distinct classifications matched by an event.

        Results use the same deterministic ranking as ``classify`` so the
        first item is always the legacy best classification. Multiple phrases
        belonging to the same category/subtype rule are represented by one
        EventClassification with all matched phrases attached.
        """
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

            classification = EventClassification(
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

            classification = self._resolve_generic_absence(
                classification,
                searchable_text,
            )
            matches.append(classification)

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

        return matches

    def _resolve_generic_absence(
        self,
        classification: EventClassification,
        searchable_text: str,
    ) -> EventClassification:
        """Avoid inferring injury when a report only says a player won't play."""
        if (
            classification.category != "injury"
            or classification.subtype != "ruled_out"
        ):
            return classification

        matched_generic_absence = any(
            normalize_event_text(phrase) in self.GENERIC_ABSENCE_PHRASES
            for phrase in classification.matched_rules
        )
        has_injury_context = any(
            normalize_event_text(phrase) in searchable_text
            for phrase in self.INJURY_CONTEXT_PHRASES
        )

        if not matched_generic_absence or has_injury_context:
            return classification

        return EventClassification(
            category="availability",
            subtype="ruled_out",
            polarity="negative",
            impact=-0.70,
            confidence=0.96,
            matched_rules=classification.matched_rules,
            metadata={
                "classifier": "deterministic_rules",
                "reason": "generic_absence_without_injury_context",
            },
        )

    @staticmethod
    def _unknown_classification() -> EventClassification:
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
