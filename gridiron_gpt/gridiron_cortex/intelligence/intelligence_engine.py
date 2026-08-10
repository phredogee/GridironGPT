from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.intelligence_context import IntelligenceContext
from gridiron_cortex.intelligence.analyzers.contradiction_analyzer import (
    ContradictionDetector,
)
from gridiron_cortex.intelligence.analyzers.reasoning_analyzer import (
    ReasoningEngine,
)
from gridiron_cortex.intelligence.analyzers.trend_analyzer import (
    TrendAnalyzer,
)
from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)

class IntelligenceEngine:

    def __init__(self):
        self.contradiction_detector = ContradictionDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.reasoning_engine = ReasoningEngine()

    def evaluate(
        self,
        context: EngineContext,
    ) -> IntelligenceContext:

        intelligence = IntelligenceContext()

        if context.canonical_event is not None:
            intelligence.contradiction = (
                self.contradiction_detector.evaluate(
                    context.canonical_event
                )
            )
        else:
            intelligence.contradiction = ContradictionResult()

        intelligence.trend = (
            self.trend_analyzer.evaluate(context)
        )

        context.contradiction = intelligence.contradiction

        intelligence.reasoning = self.reasoning_engine.evaluate(
            context
        )

        intelligence.confidence = (
            intelligence.reasoning.confidence
        )

        return intelligence
