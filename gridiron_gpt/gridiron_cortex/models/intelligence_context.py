from dataclasses import dataclass

from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)
from gridiron_cortex.models.reasoning_result import (
    ReasoningResult,
)
from gridiron_cortex.models.trend_result import (
    TrendResult,
)


@dataclass
class IntelligenceContext:
    contradiction: ContradictionResult | None = None

    trend: TrendResult | None = None

    reasoning: ReasoningResult | None = None
    confidence: float = 0.0
