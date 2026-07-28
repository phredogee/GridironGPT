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

        positives = self._find_matches(
            evidence,
            self.POSITIVE_KEYWORDS,
        )

        negatives = self._find_matches(
            evidence,
            self.NEGATIVE_KEYWORDS,
        )

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
                {
                    evidence.source
                    for evidence in canonical_event.evidence
                }
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

    def _find_matches(
        self,
        evidence: list[str],
        keywords: set[str],
    ) -> list[str]:
        matches = set()

        for headline in evidence:
            normalized = headline.lower()

            for keyword in keywords:
                if keyword in normalized:
                    matches.add(keyword)

        return sorted(matches)
