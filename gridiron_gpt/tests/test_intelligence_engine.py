from gridiron_cortex.intelligence.intelligence_engine import (
    IntelligenceEngine,
)
from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.intelligence_context import (
    IntelligenceContext,
)
from gridiron_cortex.models.raw_event import RawEvent


def build_raw_event() -> RawEvent:
    return RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
    )


def test_returns_intelligence_context():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert isinstance(result, IntelligenceContext)


def test_defaults_are_empty():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.contradiction is not None
    assert result.contradiction.has_conflict is False
    assert result.contradiction.severity == 0.0
    assert result.trend is not None
    assert result.reasoning is not None
    assert result.confidence == 0.0

def test_has_reasoning_engine():
    engine = IntelligenceEngine()

    assert engine.reasoning_engine is not None

def test_has_trend_analyzer():
    engine = IntelligenceEngine()

    assert engine.trend_analyzer is not None

def test_has_contradiction_detector():
    engine = IntelligenceEngine()

    assert engine.contradiction_detector is not None

def test_returns_default_confidence():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.confidence == 0.0

def test_evaluate_populates_trend():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.trend is not None
    assert result.trend.direction == "stable"
    assert result.trend.observations == 0

def test_evaluate_populates_contradiction():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.contradiction is not None

def test_evaluate_populates_reasoning():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.reasoning is not None

def test_confidence_matches_reasoning():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = IntelligenceEngine().evaluate(context)

    assert result.confidence == result.reasoning.confidence
