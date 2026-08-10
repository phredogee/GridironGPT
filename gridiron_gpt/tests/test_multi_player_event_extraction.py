from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.normalize.event_normalizer import EventNormalizer
from gridiron_gpt.ingestion.sources.rss import RSSSourceAdapter


class FakeEntry(dict):
    pass


def test_rss_entry_emits_one_record_per_resolved_player(monkeypatch):
    adapter = RSSSourceAdapter(
        feed_url="https://example.com/feed",
        source_name="Example NFL",
    )

    monkeypatch.setattr(
        "gridiron_gpt.ingestion.sources.rss.extract_players_from_text",
        lambda text: [
            {
                "player": "Bijan Robinson",
                "team": "ATL",
                "position": "RB",
                "confidence": 1.0,
                "matched_alias": "Bijan Robinson",
            },
            {
                "player": "Jahmyr Gibbs",
                "team": "DET",
                "position": "RB",
                "confidence": 1.0,
                "matched_alias": "Jahmyr Gibbs",
            },
        ],
    )

    entry = FakeEntry(
        id="article-123",
        title="Robinson and Gibbs among preseason hold-ins",
        summary="Two star running backs remain limited.",
        link="https://example.com/article-123",
        published="2026-08-02T12:00:00Z",
    )

    records = adapter._records_from_entry(entry)

    assert len(records) == 2
    assert {record.player for record in records} == {
        "Bijan Robinson",
        "Jahmyr Gibbs",
    }
    assert {record.source_id for record in records} == {"article-123"}
    assert all(
        record.metadata["article_source_id"] == "article-123"
        for record in records
    )
    assert all(
        record.metadata["matched_player_count"] == 2
        for record in records
    )


def test_multi_player_records_normalize_to_distinct_fingerprints():
    normalizer = EventNormalizer()

    first = SourceRecord(
        source="Example NFL",
        source_id="article-123",
        headline="Robinson and Gibbs among preseason hold-ins",
        player="Bijan Robinson",
        team="ATL",
        position="RB",
        url="https://example.com/article-123",
    )
    second = SourceRecord(
        source="Example NFL",
        source_id="article-123",
        headline="Robinson and Gibbs among preseason hold-ins",
        player="Jahmyr Gibbs",
        team="DET",
        position="RB",
        url="https://example.com/article-123",
    )

    first_event = normalizer.normalize(first)
    second_event = normalizer.normalize(second)

    assert first_event.evidence["source_id"] == "article-123"
    assert second_event.evidence["source_id"] == "article-123"
    assert first_event.fingerprint() != second_event.fingerprint()


def test_same_article_and_player_remains_duplicate_identity():
    first = RawEvent(
        headline="Bijan Robinson remains limited",
        source="Example NFL",
        player="Bijan Robinson",
        team="ATL",
        url="https://example.com/article-123",
        evidence={"source_id": "article-123"},
    )
    edited = RawEvent(
        headline="Bijan Robinson still limited at practice",
        source="Example NFL",
        player="Bijan Robinson",
        team="ATL",
        url="https://example.com/article-123?updated=1",
        evidence={"source_id": "article-123"},
    )

    assert first.fingerprint() == edited.fingerprint()


def test_unresolved_article_identity_stays_provider_scoped():
    first = RawEvent(
        headline="General NFL feature",
        source="Example NFL",
        url="https://example.com/article-999",
        evidence={"source_id": "article-999"},
    )
    edited = RawEvent(
        headline="Updated general NFL feature",
        source="Example NFL",
        url="https://example.com/article-999?updated=1",
        evidence={"source_id": "article-999"},
    )

    assert first.fingerprint() == edited.fingerprint()
