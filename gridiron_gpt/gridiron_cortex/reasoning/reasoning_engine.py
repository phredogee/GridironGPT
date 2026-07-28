from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.reasoning_result import (
    ReasoningResult,
)
from gridiron_cortex.understand.source_reliability import (
    SourceReliability,
)

class ReasoningEngine:

    MINIMUM_SOURCES = 2

    def __init__(self):
        self.reliability = SourceReliability()

    def _average_reliability(
        self,
        sources: list[str],
    ) -> float:

        if not sources:
            return 0.0

        scores = [
            self.reliability.score(source)
            for source in sources
        ]

        return sum(scores) / len(scores)

    def evaluate(
        self,
        context: EngineContext,
    ) -> ReasoningResult:


        canonical = context.canonical_event

        if canonical is None:
            return ReasoningResult(
                confidence=0.0,
                certainty="unknown",
                summary="No canonical event available.",
                concerns=[
                    "No evidence has been aggregated."
                ],
            )

        source_count = len(canonical.sources)

        average_reliability = self._average_reliability(
            canonical.sources
        )

        if source_count < self.MINIMUM_SOURCES:
            return ReasoningResult(
                confidence=canonical.confidence,
                certainty="low",
                summary="Limited supporting evidence.",
                concerns=[
                    "Only one source has reported this event."
                ],
                recommendations=[
                    "Wait for additional corroboration."
                ],
            )

        if average_reliability >= 0.90:
            certainty = "high"

        elif average_reliability >= 0.80:
            certainty = "moderate"

        else:
            certainty = "low"

        confidence = canonical.confidence
        concerns = []

        contradiction = context.contradiction

        if (
            contradiction is not None
            and contradiction.has_conflict
        ):
            concerns.append(
                contradiction.explanation
            )

            if certainty == "high":
                certainty = "moderate"

            elif certainty == "moderate":
                certainty = "low"

            confidence = max(
                confidence - contradiction.confidence_penalty,
                0.0,
            )

        return ReasoningResult(
            confidence=confidence,
            certainty=certainty,
            average_reliability=average_reliability,
            summary="Evidence quality evaluated.",
            supporting_evidence=[
                f"{source_count} independent sources",
                f"Average reliability: {average_reliability:.2f}",
            ],
            concerns=concerns,
        )
