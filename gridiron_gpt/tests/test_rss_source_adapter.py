from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.sources.rss import (
    RSSSourceAdapter,
)


def test_rss_adapter_source_name():
    adapter = RSSSourceAdapter(
        feed_url="https://example.com/feed",
        source_name="NBC Sports",
    )

    assert adapter.source_name == "NBC Sports"


def test_rss_adapter_extracts_url_text():
    result = RSSSourceAdapter._extract_url_text(
        "https://example.com/"
        "texans-tank-dell-returns-to-practice"
    )

    assert result == (
        "texans tank dell returns to practice"
    )


def test_rss_adapter_builds_unresolved_record():
    adapter = RSSSourceAdapter(
        feed_url="https://example.com/feed",
        source_name="ESPN",
    )

    entry = {
        "title": "Texans announce roster update",
        "summary": "Team news from practice.",
        "link": "https://example.com/team-update",
        "published": "2026-08-01T12:00:00Z",
    }

    records = adapter._records_from_entry(entry)

    assert len(records) == 1

    record = records[0]

    assert isinstance(record, SourceRecord)
    assert record.source == "ESPN"
    assert record.headline == entry["title"]
    assert record.summary == entry["summary"]
    assert record.published_at == entry["published"]
    assert record.player is None


def test_rss_adapter_does_not_interpret_fantasy_impact():
    adapter = RSSSourceAdapter(
        feed_url="https://example.com/feed",
    )

    entry = {
        "title": "Player injured and ruled out",
        "summary": "Player suffered an injury.",
        "link": "https://example.com/injury",
    }

    record = adapter._records_from_entry(entry)[0]

    assert not hasattr(
        record,
        "fantasy_impact",
    )
    assert not hasattr(
        record,
        "article_relevance",
    )
