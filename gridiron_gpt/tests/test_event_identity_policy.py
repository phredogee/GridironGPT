import json
from pathlib import Path

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.remember.json_event_repository import (
    JsonEventRepository,
)
from gridiron_cortex.understand.evidence_aggregator import (
    EvidenceAggregator,
)


def test_source_id_is_primary_provider_identity():
    first = RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/old-url",
        evidence={"source_id": "article-123"},
    )
    edited = RawEvent(
        headline="Tank Dell back at practice for Houston.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/new-url",
        evidence={"source_id": "article-123"},
    )

    assert first.fingerprint() == edited.fingerprint()


def test_url_is_stable_identity_when_source_id_is_missing():
    first = RawEvent(
        headline="Tank Dell returns to practice.",
        source="NBC Sports",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/tank-dell-practice",
    )
    edited = RawEvent(
        headline="Tank Dell returns to Houston practice.",
        source="NBC Sports",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/tank-dell-practice",
    )

    assert first.fingerprint() == edited.fingerprint()


def test_same_day_cross_source_reports_merge():
    aggregator = EvidenceAggregator()

    espn_event = RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        published_at="2026-08-02T09:00:00-05:00",
        url="https://example.com/espn/tank-dell-practice",
    )
    nbc_event = RawEvent(
        headline="Tank Dell returned to practice with Houston.",
        source="NBC Sports",
        player="Tank Dell",
        team="HOU",
        published_at="Sun, 02 Aug 2026 14:30:00 GMT",
        url="https://example.com/nbc/tank-dell-practice",
    )

    first = aggregator.add(espn_event)
    second = aggregator.add(nbc_event)

    assert first is second
    assert second.source_count == 2
    assert set(second.sources) == {"ESPN", "NBC Sports"}


def test_same_subtype_on_different_dates_does_not_merge():
    aggregator = EvidenceAggregator()

    first_event = RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        published_at="2026-08-02T09:00:00-05:00",
        url="https://example.com/espn/tank-dell-practice-aug-2",
    )
    later_event = RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        published_at="2026-08-16T09:00:00-05:00",
        url="https://example.com/espn/tank-dell-practice-aug-16",
    )

    first = aggregator.add(first_event)
    second = aggregator.add(later_event)

    assert first is not second
    assert first.event_key != second.event_key


def test_repository_recognizes_legacy_record_using_current_identity(
    tmp_path: Path,
):
    file_path = tmp_path / "events.jsonl"
    repository = JsonEventRepository(file_path)

    event = RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/espn/tank-dell-practice",
    )

    legacy_record = {
        "headline": event.headline,
        "source": event.source,
        "player": event.player,
        "team": event.team,
        "summary": None,
        "event_type": None,
        "published_at": None,
        "url": event.url,
        "sentiment": None,
        "impact_score": None,
        "confidence": None,
        "evidence": {},
        "player_id": None,
        "position": None,
        "fingerprint": "legacy-hash-value",
    }

    file_path.write_text(
        json.dumps(legacy_record) + "\n",
        encoding="utf-8",
    )

    assert repository.contains(event.fingerprint())
