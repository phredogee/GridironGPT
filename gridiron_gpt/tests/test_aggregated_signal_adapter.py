from gridiron_gpt.intelligence.aggregated_signal_adapter import (
    aggregate_to_raw_event,
)

def test_aggregate_to_raw_event():
    aggregate = {
        "player_name": "Patrick Mahomes",
        "team": "KC",
        "source": "nflverse",
        "signal_type": "production",
        "sentiment": "positive",
        "impact_score": 0.84,
        "confidence": 0.93,
        "metric": "passing_yards",
        "trend_classification": "confirmed",
        "weeks": [2, 3, 4],
        "methods": [
            "weekly_delta",
            "rolling_baseline",
        ],
        "evidence_count": 4,
        "reasons": [
            "Passing yards remained above baseline."
        ],
    }

    event = aggregate_to_raw_event(aggregate)

    assert event.headline == (
        "Patrick Mahomes passing yards increased; "
        "confirmed production trend"
    )
    assert event.source == "nflverse"
    assert event.player == "Patrick Mahomes"
    assert event.team == "KC"
    assert event.event_type == "production_trend"
    assert event.published_at is None
    assert event.url is None
    assert event.sentiment == "positive"
    assert event.impact_score == 0.84
    assert event.confidence == 0.93
    assert event.evidence["metric"] == "passing_yards"
    assert event.evidence["classification"] == "confirmed"
    assert event.evidence["evidence_count"] == 4
