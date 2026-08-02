from pathlib import Path

from gridiron_cortex.models.canonical_event import (
    CanonicalEvent,
)
from gridiron_cortex.models.source_evidence import (
    SourceEvidence,
)
from gridiron_cortex.remember.json_canonical_event_repository import (
    JsonCanonicalEventRepository,
)


def make_event(
    confidence: float = 0.80,
    source: str = "ESPN",
) -> CanonicalEvent:
    return CanonicalEvent(
        event_key="tank-dell-recovery",
        player="Tank Dell",
        team="HOU",
        category="availability",
        subtype="returned_to_practice",
        polarity="positive",
        impact=0.8,
        confidence=confidence,
        evidence=[
            SourceEvidence(
                headline="Tank Dell returns to practice.",
                source=source,
                category="availability",
                subtype="returned_to_practice",
                confidence=confidence,
            )
        ],
    )


def test_repository_saves_and_loads_event(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )

    repository.save(make_event())

    loaded = repository.get(
        "tank-dell-recovery"
    )

    assert loaded is not None
    assert loaded.player == "Tank Dell"
    assert loaded.source_count == 1
    assert loaded.sources == ["ESPN"]


def test_repository_returns_latest_snapshot(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )

    repository.save(
        make_event(
            confidence=0.80,
            source="ESPN",
        )
    )

    updated = make_event(
        confidence=0.95,
        source="ESPN",
    )
    updated.evidence.append(
        SourceEvidence(
            headline="Dell fully participates.",
            source="NBC Sports",
            category="availability",
            subtype="returned_to_practice",
            confidence=0.90,
        )
    )

    repository.save(updated)

    loaded = repository.get(
        "tank-dell-recovery"
    )

    assert loaded is not None
    assert loaded.confidence == 0.95
    assert loaded.source_count == 2
    assert loaded.sources == [
        "ESPN",
        "NBC Sports",
    ]


def test_repository_preserves_history(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )

    repository.save(make_event(confidence=0.80))
    repository.save(make_event(confidence=0.90))

    history = repository.get_history(
        "tank-dell-recovery"
    )

    assert len(history) == 2
    assert history[0].confidence == 0.80
    assert history[1].confidence == 0.90


def test_repository_returns_none_for_unknown_event(
    tmp_path: Path,
):
    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )

    assert repository.get("missing") is None
