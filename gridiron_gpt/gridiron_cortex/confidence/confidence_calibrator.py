from gridiron_cortex.models.confidence_result import (
    ConfidenceResult,
)


class ConfidenceCalibrator:
    """
    Combines multiple confidence measurements into one
    calibrated confidence score for the engine.
    """

    SIGNAL_WEIGHT = 0.60
    EVIDENCE_WEIGHT = 0.40

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp confidence to the range [0.0, 1.0]."""
        return max(0.0, min(1.0, value))

    def calibrate(
        self,
        classifier_confidence: float,
        evidence_confidence: float,
    ) -> ConfidenceResult:
        """
        Combine classifier confidence and evidence trust into
        one calibrated confidence value.
        """

        classifier_confidence = self._clamp(
            classifier_confidence
        )
        evidence_confidence = self._clamp(
            evidence_confidence
        )

        final_confidence = (
            classifier_confidence * self.SIGNAL_WEIGHT
            + evidence_confidence * self.EVIDENCE_WEIGHT
        )

        final_confidence = self._clamp(final_confidence)

        return ConfidenceResult(
            classifier_confidence=classifier_confidence,
            evidence_confidence=evidence_confidence,
            final_confidence=final_confidence,
            explanation=(
                "Calibrated from classifier confidence "
                "and evidence trust."
            ),
        )
