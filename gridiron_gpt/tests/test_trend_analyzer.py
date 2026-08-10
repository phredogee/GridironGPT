from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.trend_result import TrendResult
from gridiron_cortex.reasoning.trend_analyzer import TrendAnalyzer
from gridiron_cortex.models.historical_snapshot import HistoricalSnapshot
from gridiron_cortex.models.raw_event import RawEvent


def build_raw_event() -> RawEvent:
    return RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
    )


def build_context(
    scores: list[float],
) -> EngineContext:
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    context.history = [
        HistoricalSnapshot(
            timestamp=f"2026-07-{index + 1:02d}T12:00:00+00:00",
            overall_score=score,
            confidence=0.80,
        )
        for index, score in enumerate(scores)
    ]

    return context

def test_returns_trend_result():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = TrendAnalyzer().evaluate(context)

    assert isinstance(result, TrendResult)

def test_defaults_to_stable():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = TrendAnalyzer().evaluate(context)

    assert result.direction == "stable"
    assert result.confidence_delta == 0.0
    assert result.explanation == ""

def test_empty_history_is_stable():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = TrendAnalyzer().evaluate(context)

    assert result.direction == "stable"

def test_history_counts_observations():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    context.history = [
        HistoricalSnapshot(
            timestamp="2026-07-01",
            overall_score=60,
            confidence=0.90,
        ),
        HistoricalSnapshot(
            timestamp="2026-07-02",
            overall_score=62,
            confidence=0.91,
        ),
        HistoricalSnapshot(
            timestamp="2026-07-03",
            overall_score=64,
            confidence=0.92,
        ),
    ]

    result = TrendAnalyzer().evaluate(context)

    assert result.observations == 3
