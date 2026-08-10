from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.raw_event import RawEvent


def test_structured_positive_event_reaches_recommendation(tmp_path):
    cortex = CortexFacade(data_directory=tmp_path)

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
            "metric": "targets",
            "classification": "confirmed",
            "evidence_count": 2,
            "sources": ["nflverse"],
            "methods": [
                "weekly_delta",
                "rolling_baseline",
            ],
            "reasons": [
                "Targets increased week over week.",
                "Targets exceeded the rolling baseline.",
            ],
        },
    )

    result = cortex.process_event(event)

    assert result.signal is not None
    assert result.signal.sentiment == "positive"
    assert result.signal.impact_score == 0.82
    assert result.signal.confidence == 0.94

    assert result.score_updates
    assert result.score_updates[0].score_delta > 0

    assert result.recommendations
    assert result.recommendations[0].action in {
        "BUY",
        "WATCH",
    }

    assert "Evidence count: 2" in result.explanation
    assert "weekly_delta" in result.explanation
    assert "rolling_baseline" in result.explanation
