from dataclasses import dataclass

from gridiron_cortex.models.canonical_event import CanonicalEvent


@dataclass(frozen=True)
class EvidenceAssessment:
    source_count: int
    independent_source_count: int

    agreement_score: float
    conflict_score: float
    source_diversity: float
    source_quality: float

    trust_score: float
    consensus_level: str
    developing_story: bool


class EvidenceAnalyzer:
    """Evaluate the strength and consistency of canonical evidence."""

    def analyze(
        self,
        event: CanonicalEvent,
    ) -> EvidenceAssessment:
        evidence = event.evidence

        if not evidence:
            return EvidenceAssessment(
                source_count=0,
                independent_source_count=0,
                agreement_score=0.0,
                conflict_score=0.0,
                source_diversity=0.0,
                source_quality=0.0,
                trust_score=0.0,
                consensus_level="none",
                developing_story=True,
            )

        normalized_sources = {
            item.source.strip().casefold()
            for item in evidence
            if item.source.strip()
        }

        independent_source_count = len(normalized_sources)
        source_count = len(evidence)

        matching_evidence = [
            item
            for item in evidence
            if (
                item.category == event.category
                and item.subtype == event.subtype
            )
        ]

        agreement_score = len(matching_evidence) / source_count
        conflict_score = 1.0 - agreement_score

        source_diversity = min(
            independent_source_count / 3.0,
            1.0,
        )

        source_quality = sum(
            item.confidence
            for item in evidence
        ) / source_count

        trust_score = (
            agreement_score * 0.40
            + source_quality * 0.35
            + source_diversity * 0.25
        )

        trust_score = max(
            0.0,
            min(trust_score, 1.0),
        )

        consensus_level = self._determine_consensus_level(
            agreement_score=agreement_score,
            independent_source_count=independent_source_count,
        )

        developing_story = (
            independent_source_count < 2
            or conflict_score >= 0.34
        )

        return EvidenceAssessment(
            source_count=source_count,
            independent_source_count=independent_source_count,
            agreement_score=round(agreement_score, 4),
            conflict_score=round(conflict_score, 4),
            source_diversity=round(source_diversity, 4),
            source_quality=round(source_quality, 4),
            trust_score=round(trust_score, 4),
            consensus_level=consensus_level,
            developing_story=developing_story,
        )

    @staticmethod
    def _determine_consensus_level(
        agreement_score: float,
        independent_source_count: int,
    ) -> str:
        if independent_source_count == 0:
            return "none"

        if independent_source_count == 1:
            return "single_source"

        if agreement_score >= 0.90:
            return "strong"

        if agreement_score >= (2 / 3):
            return "moderate"

        if agreement_score >= 0.50:
            return "mixed"

        return "conflicted"
