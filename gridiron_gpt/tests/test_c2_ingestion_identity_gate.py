from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.remember.json_canonical_event_repository import (
    JsonCanonicalEventRepository,
)
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.normalize.event_normalizer import EventNormalizer


def make_record(
    *,
    source: str,
    headline: str,
    source_id: str,
    url: str,
) -> SourceRecord:
    return SourceRecord(
        source=source,
        headline=headline,
        player="Tank Dell",
        team="HOU",
        position="WR",
        published_at="2026-08-02T12:00:00Z",
        url=url,
        source_id=source_id,
    )


def test_c2_identity_and_persistence_gate(
    tmp_path: Path,
):
    normalizer = EventNormalizer()

    espn = normalizer.normalize(
        make_record(
            source="ESPN",
            headline="Tank Dell returns to practice.",
            source_id="espn-123",
            url="https://example.com/espn/tank-dell",
        )
    )

    espn_edited = normalizer.normalize(
        make_record(
            source="ESPN",
            headline="Tank Dell returns to practice with Houston.",
            source_id="espn-123",
            url="https://example.com/espn/tank-dell-updated",
        )
    )

    nbc = normalizer.normalize(
        make_record(
            source="NBC Sports",
            headline="Tank Dell returned to practice with Houston.",
            source_id="nbc-456",
            url="https://example.com/nbc/tank-dell",
        )
    )

    first_cortex = CortexFacade(data_directory=tmp_path)

    first_result = first_cortex.process_event(espn)
    duplicate_result = first_cortex.process_event(espn_edited)

    assert first_result.signal is not None
    assert duplicate_result.signal is None
    assert duplicate_result.explanation == "Duplicate event ignored."

    restarted_cortex = CortexFacade(data_directory=tmp_path)
    corroborated_result = restarted_cortex.process_event(nbc)

    assert corroborated_result.signal is not None
    assert corroborated_result.signal.source_count == 2
    assert set(corroborated_result.signal.sources) == {
        "ESPN",
        "NBC Sports",
    }

    repository = JsonCanonicalEventRepository(
        tmp_path / "canonical_events.jsonl"
    )

    history = repository.get_history(
        corroborated_result.signal.evidence[
            "event_classification"
        ]["event_key"]
        if "event_key"
        in corroborated_result.signal.evidence.get(
            "event_classification",
            {},
        )
        else restarted_cortex.engine.evidence_aggregator._build_event_key(
            nbc,
            corroborated_result.signal.evidence[
                "event_classification"
            ]["category"],
            corroborated_result.signal.evidence[
                "event_classification"
            ]["subtype"],
        )
    )

    assert len(history) == 2
    assert history[0].source_count == 1
    assert history[1].source_count == 2
