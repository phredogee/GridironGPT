from apps.streamlit.pages.mission_control import MissionPlayerContext, build_raw_event_from_signal, latest_signal


def _context():
    return MissionPlayerContext(
        player="Tank Dell",
        team="HOU",
        score=1.25,
        signal_count=2,
        entity_id="tank-dell",
    )


def test_latest_signal_returns_most_recent_item():
    data = {"signals": [{"headline": "old"}, {"headline": "new"}]}
    assert latest_signal(data)["headline"] == "new"


def test_build_raw_event_from_positive_signal():
    signal = {
        "headline": "Tank Dell returns to practice",
        "source": "ESPN",
        "value": 0.75,
        "impact": "opportunity",
        "story_hash": "story-123",
        "published_at": "2026-08-04T12:00:00+00:00",
    }
    event = build_raw_event_from_signal(_context(), signal)
    assert event.player == "Tank Dell"
    assert event.team == "HOU"
    assert event.sentiment == "positive"
    assert event.impact_score == 0.75
    assert event.event_type == "opportunity"
    assert event.evidence["source_id"] == "story-123"


def test_build_raw_event_from_negative_signal():
    event = build_raw_event_from_signal(
        _context(),
        {"headline": "Tank Dell limited", "source": "NBC", "value": -0.5},
    )
    assert event.sentiment == "negative"
    assert event.impact_score == -0.5
