import requests

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


def test_rss_adapter_fetch_uses_explicit_http_timeout(monkeypatch):
    observed = {}

    class FakeResponse:
        content = b"<rss><channel></channel></rss>"

        def raise_for_status(self):
            observed["raised"] = True

    def fake_get(url, *, timeout, headers):
        observed["url"] = url
        observed["timeout"] = timeout
        observed["headers"] = headers
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    adapter = RSSSourceAdapter(
        feed_url="https://example.com/feed",
        source_name="ESPN",
        request_timeout_seconds=4.5,
    )

    assert adapter.fetch() == []
    assert observed["url"] == "https://example.com/feed"
    assert observed["timeout"] == 4.5
    assert observed["raised"] is True
    assert observed["headers"]["User-Agent"].startswith("GridironGPT/")


def test_rss_adapter_rejects_nonpositive_timeout():
    try:
        RSSSourceAdapter(
            feed_url="https://example.com/feed",
            request_timeout_seconds=0,
        )
    except ValueError as exc:
        assert str(exc) == "request_timeout_seconds must be positive"
    else:
        raise AssertionError("Expected ValueError for nonpositive RSS timeout")
