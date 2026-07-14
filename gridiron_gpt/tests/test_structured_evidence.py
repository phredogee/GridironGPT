from gridiron_cortex.engine.signal_processor import SignalProcessor
from gridiron_cortex.models.raw_event import RawEvent


def test_signal_processor_uses_structured_intelligence():
    event = RawEvent(
        headline=(
            "Test Player targets increased; "
            "confirmed opportunity trend"
        ),
        source="nflverse",
        player="Test Player",
        team="DAL",
        event_type="opportunity_trend",
        sentiment="positive",
        impact_score=0.82,
        confidence=0.94,
        evidence={
            "evidence_count": 2,
            "sources": ["nflverse"],
            "methods": [
                "weekly_delta",
                "rolling_baseline",
            ],
        },
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.82
    assert signal.confidence == 0.94
    assert signal.evidence["evidence_count"] == 2


def test_signal_processor_preserves_keyword_fallback():
    event = RawEvent(
        headline="Test Player returned healthy and active",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 1.0
    assert signal.evidence == {}
