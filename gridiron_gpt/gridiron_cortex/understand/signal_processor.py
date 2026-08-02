import re
from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.signal import Signal
from gridiron_cortex.understand.football_language import (
    CONCEPTS,
    FootballConcept,
)
from gridiron_cortex.understand.event_classifier import EventClassifier
from gridiron_cortex.understand.statistical_event_interpreter import (
    StatisticalEventInterpreter,
)


class SignalProcessor:
    """Convert a resolved event into a fantasy-relevant signal."""

    def __init__(self):
        self.classifier = EventClassifier()
        self.statistical_interpreter = StatisticalEventInterpreter()

    POSITIVE_KEYWORDS = [
        "returns", "returned", "first-team", "starter", "cleared",
        "healthy", "full participant", "active", "breakout",
    ]

    NEGATIVE_KEYWORDS = [
        "injured", "injury", "out", "questionable", "doubtful",
        "limited", "missed", "misses practice", "setback",
        "suspended", "bench", "benched",
    ]

    CATEGORY_KEYWORDS = {
        "injury": ["injured", "injury", "out", "questionable", "doubtful", "setback"],
        "recovery": ["returns", "returned", "cleared", "healthy", "full participant"],
        "opportunity": ["first-team", "starter", "starting", "increased reps", "more snaps"],
        "depth_chart": ["bench", "benched", "promoted", "demoted", "depth chart"],
        "suspension": ["suspended", "suspension"],
    }

    def process(
        self,
        event: RawEvent,
        entities: list[Entity],
        canonical_event: CanonicalEvent | None = None,
    ):
        classification = self.classifier.classify(event)
        headline = event.headline
        headline_lower = headline.casefold()

        positive_hits = self._find_keyword_hits(headline_lower, self.POSITIVE_KEYWORDS)
        negative_hits = self._find_keyword_hits(headline_lower, self.NEGATIVE_KEYWORDS)
        matched_concepts = self._match_concepts(headline_lower)
        evidence = dict(event.evidence)

        has_structured_intelligence = (
            event.sentiment is not None
            or event.impact_score is not None
            or event.confidence is not None
        )

        if self.statistical_interpreter.can_interpret(event):
            interpretation = self.statistical_interpreter.interpret(event)
            sentiment = interpretation.sentiment
            impact_score = interpretation.impact_score
            confidence = interpretation.confidence
            positive_hits = []
            negative_hits = []
            evidence["statistical_interpretation"] = {
                "indicators": interpretation.indicators,
                "reasons": interpretation.reasons,
                "method": "structured_player_stats",
            }
            signal_category = "performance"
            signal_type = "statistics"

        elif has_structured_intelligence:
            sentiment = event.sentiment or "neutral"
            impact_score = float(event.impact_score or 0.0)
            confidence = float(event.confidence or 0.0)
            signal_category = self.classify_signal_category(headline)
            signal_type = event.event_type or "news"

        elif matched_concepts:
            sentiment, impact_score, confidence = self._interpret_concepts(matched_concepts)
            evidence.update(self._build_concept_evidence(matched_concepts))
            positive_hits = self._merge_hits(
                positive_hits,
                self._concept_hits(matched_concepts, sentiment="positive"),
            )
            negative_hits = self._merge_hits(
                negative_hits,
                self._concept_hits(matched_concepts, sentiment="negative"),
            )
            signal_category = self.classify_signal_category(headline)
            signal_type = event.event_type or "news"

        elif classification.category != "unknown":
            sentiment = classification.polarity
            impact_score = classification.impact
            confidence = classification.confidence
            signal_category = self.classify_signal_category(headline)
            signal_type = event.event_type or "news"

        else:
            sentiment = self._keyword_sentiment(
                positive_hits=positive_hits,
                negative_hits=negative_hits,
            )
            impact_score = self._keyword_impact(sentiment)
            confidence = 1.0
            signal_category = self.classify_signal_category(headline)
            signal_type = event.event_type or "news"

        if classification.category != "unknown" and signal_type != "statistics":
            evidence["event_classification"] = {
                "category": classification.category,
                "subtype": classification.subtype,
                "polarity": classification.polarity,
                "confidence": classification.confidence,
                "impact": classification.impact,
                "matched_rules": classification.matched_rules,
            }

        if canonical_event is not None:
            source_count = len(canonical_event.sources)
            sources = list(canonical_event.sources)
            corroboration_confidence = canonical_event.confidence
        else:
            source_count = 1
            sources = [event.source] if event.source else []
            corroboration_confidence = confidence

        return Signal(
            headline=headline,
            entities=entities,
            sentiment=sentiment,
            impact_score=round(impact_score, 3),
            positive_hits=positive_hits,
            negative_hits=negative_hits,
            confidence=round(confidence, 3),
            source_count=source_count,
            sources=sources,
            corroboration_confidence=corroboration_confidence,
            signal_category=signal_category,
            signal_type=signal_type,
            evidence=evidence,
        )

    @classmethod
    def _find_keyword_hits(cls, headline: str, keywords: list[str]) -> list[str]:
        return [keyword for keyword in keywords if cls._phrase_matches(headline, keyword)]

    @classmethod
    def _match_concepts(cls, headline: str) -> list[FootballConcept]:
        return [
            concept
            for concept in CONCEPTS
            if any(cls._phrase_matches(headline, keyword) for keyword in concept.keywords)
        ]

    @staticmethod
    def _phrase_matches(headline: str, phrase: str) -> bool:
        normalized_phrase = phrase.strip().casefold()
        if not normalized_phrase:
            return False
        pattern = re.escape(normalized_phrase).replace(r"\ ", r"\s+")
        return bool(re.search(rf"(?<!\w){pattern}(?!\w)", headline))

    @staticmethod
    def _interpret_concepts(concepts: list[FootballConcept]) -> tuple[str, float, float]:
        total_impact = sum(concept.impact for concept in concepts)
        sentiment = "positive" if total_impact > 0 else "negative" if total_impact < 0 else "mixed"
        impact_score = max(-1.0, min(total_impact, 1.0))
        confidence = sum(concept.confidence for concept in concepts) / len(concepts)
        return sentiment, impact_score, confidence

    @staticmethod
    def _build_concept_evidence(concepts: list[FootballConcept]) -> dict:
        return {
            "evidence_count": len(concepts),
            "methods": ["football_concept_matching"],
            "classification": concepts[0].name if len(concepts) == 1 else "multi_concept",
            "categories": list(dict.fromkeys(concept.category for concept in concepts)),
            "concepts": [
                {
                    "name": concept.name,
                    "category": concept.category,
                    "sentiment": concept.sentiment,
                    "impact": concept.impact,
                    "confidence": concept.confidence,
                }
                for concept in concepts
            ],
            "reasons": [
                f"Detected football concept '{concept.name}' in category '{concept.category}'."
                for concept in concepts
            ],
        }

    @staticmethod
    def _concept_hits(concepts: list[FootballConcept], sentiment: str) -> list[str]:
        return [concept.name for concept in concepts if concept.sentiment == sentiment]

    @staticmethod
    def _merge_hits(first: list[str], second: list[str]) -> list[str]:
        return list(dict.fromkeys(first + second))

    @staticmethod
    def _keyword_sentiment(*, positive_hits: list[str], negative_hits: list[str]) -> str:
        if positive_hits and negative_hits:
            if len(negative_hits) > len(positive_hits):
                return "negative"
            if len(positive_hits) > len(negative_hits):
                return "positive"
            return "mixed"
        if negative_hits:
            return "negative"
        if positive_hits:
            return "positive"
        return "neutral"

    @staticmethod
    def _keyword_impact(sentiment: str) -> float:
        if sentiment == "positive":
            return 1.0
        if sentiment == "negative":
            return -1.0
        return 0.0

    @classmethod
    def classify_signal_category(cls, text: str) -> str:
        normalized = text.casefold()
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                return category
        return "general"
