from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.normalize.event_normalizer import (
    EventNormalizer,
)


def test_event_normalizer_builds_raw_event():
    record = SourceRecord(
        source="NBC Sports",
        headline="Tank Dell returns to practice.",
        published_at="2026-08-01T12:00:00Z",
        url="https://example.com/tank-dell",
        summary="Dell participated in practice.",
        player="Tank Dell",
        team="HOU",
        position="WR",
        source_id="story-123",
        metadata={
            "feed": "nfl",
        },
    )

    event = EventNormalizer().normalize(record)

    assert event.headline == record.headline
    assert event.source == "NBC Sports"
    assert event.player == "Tank Dell"
    assert event.team == "HOU"
    assert event.position == "WR"
    assert event.summary == record.summary
    assert event.published_at == record.published_at
    assert event.url == record.url

    assert event.url == record.url
    assert event.evidence["source_id"] == "story-123"
    assert event.evidence["sources"] == ["NBC Sports"]
    assert event.evidence["source_count"] == 1
    assert event.evidence["source_metadata"]["feed"] == "nfl"


def test_event_normalizer_preserves_unresolved_player():
    record = SourceRecord(
        source="ESPN",
        headline="Texans offense gets encouraging news.",
    )

    event = EventNormalizer().normalize(record)

    assert event.player is None
    assert event.team is None


def test_event_normalizer_does_not_preclassify_event():
    record = SourceRecord(
        source="NFL",
        headline="Player returns to full practice.",
    )

    event = EventNormalizer().normalize(record)

    assert event.sentiment is None
    assert event.impact_score is None
