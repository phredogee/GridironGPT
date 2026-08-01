from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)


class ContradictionDetector:
    POSITIVE_KEYWORDS = {
        "healthy",
        "activated",
        "returns",
        "full practice",
        "starting",
        "cleared",
    }

    NEGATIVE_KEYWORDS = {
        "injury",
        "out",
        "inactive",
        "ir",
        "questionable",
        "limited",
        "benched",
    }

    def _collect_evidence(
        self,
        canonical_event: CanonicalEvent,
    ) -> list[str]:
        return [
            evidence.headline
            for evidence in canonical_event.evidence
        ]

    def evaluate(
        self,
        canonical_event: CanonicalEvent,
    ) -> ContradictionResult:

        evidence = self._collect_evidence(
            canonical_event,
        )

        positives = set()
        negatives = set()

        positive_sources = set()
        negative_sources = set()

        for evidence_item in canonical_event.evidence:
            positive_matches = self._matches_keywords(
                evidence_item.headline,
                self.POSITIVE_KEYWORDS,
            )

            negative_matches = self._matches_keywords(
                evidence_item.headline,
                self.NEGATIVE_KEYWORDS,
            )

            if positive_matches:
                positives.update(positive_matches)
                positive_sources.add(evidence_item.source)

            if negative_matches:
                negatives.update(negative_matches)
                negative_sources.add(evidence_item.source)

        positives = sorted(positives)
        negatives = sorted(negatives)

        has_conflict = (
            bool(positives)
            and bool(negatives)
        )

        match_count = min(
            len(positives),
            len(negatives),
        )

        severity = min(
            match_count * 0.20,
            0.50,
        )

        confidence_penalty = min(
            match_count * 0.20,
            0.50,
        )

        conflicting_sources = []

        if has_conflict:
            conflicting_sources = sorted(
                positive_sources | negative_sources
            )

        if has_conflict:
            explanation = (
                "Conflicting evidence detected. "
                f"Positive indicators: {', '.join(positives)}. "
                f"Negative indicators: {', '.join(negatives)}."
            )
        else:
            explanation = (
                "No contradictory evidence found."
            )

        return ContradictionResult(
            has_conflict=has_conflict,
            severity=severity,
            confidence_penalty=confidence_penalty,
            conflicting_sources=conflicting_sources,
            explanation=explanation,
        )

    def _matches_keywords(
        self,
        headline: str,
        keywords: set[str],
    ) -> list[str]:
        normalized = headline.casefold()

        return sorted(
            keyword
            for keyword in keywords
            if keyword in normalized
        )

    def test_neutral_source_is_not_marked_as_conflicting():
        detector = ContradictionDetector()

        event = build_canonical_event(
            evidence=[
                build_source_evidence(
                    source="ESPN",
                    headline="Tank Dell returns to practice.",
                ),
                build_source_evidence(
                    source="NFL.com",
                    headline="Tank Dell ruled out with injury.",
                ),
                build_source_evidence(
                    source="NBC Sports",
                    headline="Tank Dell spoke with reporters.",
                ),
            ]
        )

        result = detector.evaluate(event)

        assert result.has_conflict is True
        assert set(result.conflicting_sources) == {
            "ESPN",
            "NFL.com",
        }
