from dataclasses import dataclass, field


@dataclass
class ReasoningResult:
    """
    Represents Cortex's internal assessment of the available evidence.
    """

    confidence: float = 0.0
    certainty: str = "unknown"
    summary: str = ""
    average_reliability: float = 0.0

    supporting_evidence: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
