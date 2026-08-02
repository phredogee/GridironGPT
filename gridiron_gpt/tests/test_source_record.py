from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)


def test_source_record_contains_source_evidence():
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

    assert record.source == "NBC Sports"
    assert record.headline == "Tank Dell returns to practice."
    assert record.player == "Tank Dell"
    assert record.team == "HOU"
    assert record.metadata["feed"] == "nfl"


def test_source_record_allows_unresolved_player():
    record = SourceRecord(
        source="ESPN",
        headline="Texans offense gets encouraging news.",
    )

    assert record.player is None
    assert record.team is None
    assert record.position is None


def test_source_record_does_not_require_interpretation():
    record = SourceRecord(
        source="NFL",
        headline="Player participates in practice.",
    )

    assert not hasattr(record, "fantasy_impact")
    assert not hasattr(record, "impact_score")
    assert not hasattr(record, "recommendation")
