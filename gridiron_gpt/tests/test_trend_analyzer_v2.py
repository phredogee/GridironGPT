from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.historical_snapshot import (
    HistoricalSnapshot,
)
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.reasoning.trend_analyzer import TrendAnalyzer


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


def test_empty_history_returns_stable_result():
    result = TrendAnalyzer().evaluate(
        build_context([]),
    )

    assert result.direction == "stable"
    assert result.strength == 0.0
    assert result.confidence_delta == 0.0
    assert result.observations == 0


def test_single_observation_is_insufficient():
    result = TrendAnalyzer().evaluate(
        build_context([50.0]),
    )

    assert result.direction == "stable"
    assert result.strength == 0.0
    assert result.observations == 1
    assert "Insufficient history" in result.explanation


def test_increasing_scores_produce_rising_trend():
    result = TrendAnalyzer().evaluate(
        build_context([50.0, 53.0, 56.0]),
    )

    assert result.direction == "rising"
    assert result.strength == 0.6
    assert result.confidence_delta == 6.0
    assert result.observations == 3


def test_decreasing_scores_produce_falling_trend():
    result = TrendAnalyzer().evaluate(
        build_context([60.0, 57.0, 54.0]),
    )

    assert result.direction == "falling"
    assert result.strength == 0.6
    assert result.confidence_delta == -6.0
    assert result.observations == 3


def test_small_score_change_remains_stable():
    result = TrendAnalyzer().evaluate(
        build_context([50.0, 50.3]),
    )

    assert result.direction == "stable"
    assert result.confidence_delta == 0.0


def test_strength_is_capped_at_one():
    result = TrendAnalyzer().evaluate(
        build_context([50.0, 70.0]),
    )

    assert result.direction == "rising"
    assert result.strength == 1.0
    assert result.confidence_delta == 10.0


def test_history_is_sorted_by_timestamp():
    context = EngineContext(
    raw_event=build_raw_event(),
    )
    context.history = [
        HistoricalSnapshot(
            timestamp="2026-07-03T12:00:00+00:00",
            overall_score=56.0,
            confidence=0.8,
        ),
        HistoricalSnapshot(
            timestamp="2026-07-01T12:00:00+00:00",
            overall_score=50.0,
            confidence=0.8,
        ),
        HistoricalSnapshot(
            timestamp="2026-07-02T12:00:00+00:00",
            overall_score=53.0,
            confidence=0.8,
        ),
    ]

    result = TrendAnalyzer().evaluate(context)

    assert result.direction == "rising"
    assert result.strength == 0.6
