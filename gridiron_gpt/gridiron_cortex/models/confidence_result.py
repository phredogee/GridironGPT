from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceResult:
    """Final calibrated confidence for a processed signal."""

    classifier_confidence: float
    evidence_confidence: float

    final_confidence: float

    explanation: str
