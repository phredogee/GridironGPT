from pathlib import Path

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.remember.json_canonical_event_repository import (
    JsonCanonicalEventRepository,
)
from gridiron_cortex.understand.evidence_aggregator import (
    EvidenceAggregator,
)


def make_event(
    *,
    headline: str,
    source: str,
    url: str,
) -> RawEvent:
    return RawEvent(
        headline=headline,
        source=source,
        player="Tank Dell",
        team="HOU",
        url=url,
    )


def test_new_canonical_event_is_persisted(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )
    aggregator = EvidenceAggregator(repository=repository)

    event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    canonical = aggregator.add(event)
    persisted = repository.get(canonical.event_key)

    assert persisted is not None
    assert persisted.event_key == canonical.event_key
    assert persisted.player == "Tank Dell"
    assert persisted.source_count == 1
    assert persisted.sources == ["ESPN"]


def test_canonical_event_survives_aggregator_restart(
    tmp_path: Path,
):
    file_path = tmp_path / "canonical_events.jsonl"

    first_repository = JsonCanonicalEventRepository(file_path)
    first_aggregator = EvidenceAggregator(
        repository=first_repository
    )

    espn_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )
    first_canonical = first_aggregator.add(espn_event)

    second_repository = JsonCanonicalEventRepository(file_path)
    second_aggregator = EvidenceAggregator(
        repository=second_repository
    )

    nbc_event = make_event(
        headline="Tank Dell returned to practice with Houston.",
        source="NBC Sports",
        url="https://example.com/nbc/tank-dell-practice",
    )
    second_canonical = second_aggregator.add(nbc_event)

    assert second_canonical.event_key == first_canonical.event_key
    assert second_canonical.source_count == 2
    assert set(second_canonical.sources) == {
        "ESPN",
        "NBC Sports",
    }

    persisted = second_repository.get(
        second_canonical.event_key
    )

    assert persisted is not None
    assert persisted.source_count == 2
    assert set(persisted.sources) == {
        "ESPN",
        "NBC Sports",
    }


def test_corrobating_source_creates_new_snapshot(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )
    aggregator = EvidenceAggregator(repository=repository)

    espn_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )
    nbc_event = make_event(
        headline="Tank Dell returned to practice with Houston.",
        source="NBC Sports",
        url="https://example.com/nbc/tank-dell-practice",
    )

    canonical = aggregator.add(espn_event)
    aggregator.add(nbc_event)

    history = repository.get_history(canonical.event_key)

    assert len(history) == 2
    assert history[0].source_count == 1
    assert history[1].source_count == 2
    assert history[1].confidence > history[0].confidence


def test_duplicate_evidence_does_not_create_new_snapshot(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )
    aggregator = EvidenceAggregator(repository=repository)

    event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    canonical = aggregator.add(event)
    aggregator.add(event)

    history = repository.get_history(canonical.event_key)

    assert len(history) == 1
    assert history[0].source_count == 1
