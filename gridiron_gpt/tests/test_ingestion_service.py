from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.services.ingestion_service import (
    IngestionService,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class FakeSourceAdapter(SourceAdapter):

    def __init__(
        self,
        source_name: str,
        records: list[SourceRecord],
    ):
        self._source_name = source_name
        self._records = records
        self.fetch_calls = 0

    @property
    def source_name(self) -> str:
        return self._source_name

    def fetch(self) -> list[SourceRecord]:
        self.fetch_calls += 1
        return self._records


def test_ingestion_service_normalizes_source_records():
    adapter = FakeSourceAdapter(
        source_name="Test Source",
        records=[
            SourceRecord(
                source="Test Source",
                headline="Test Player returns to practice.",
                player="Test Player",
                team="TST",
                position="WR",
            )
        ],
    )

    events = IngestionService().ingest(adapter)

    assert len(events) == 1

    event = events[0]

    assert event.source == "Test Source"
    assert event.player == "Test Player"
    assert event.team == "TST"
    assert event.position == "WR"

    assert event.sentiment is None
    assert event.impact_score is None
    assert event.confidence is None


def test_ingestion_service_handles_multiple_records():
    adapter = FakeSourceAdapter(
        source_name="Test Source",
        records=[
            SourceRecord(
                source="Test Source",
                headline="Player One update.",
                player="Player One",
            ),
            SourceRecord(
                source="Test Source",
                headline="Player Two update.",
                player="Player Two",
            ),
        ],
    )

    events = IngestionService().ingest(adapter)

    assert len(events) == 2
    assert events[0].player == "Player One"
    assert events[1].player == "Player Two"


def test_ingestion_service_handles_multiple_adapters():
    first = FakeSourceAdapter(
        source_name="Source A",
        records=[
            SourceRecord(
                source="Source A",
                headline="First event.",
            )
        ],
    )

    second = FakeSourceAdapter(
        source_name="Source B",
        records=[
            SourceRecord(
                source="Source B",
                headline="Second event.",
            )
        ],
    )

    events = IngestionService().ingest_many(
        [first, second]
    )

    assert len(events) == 2
    assert events[0].source == "Source A"
    assert events[1].source == "Source B"


def test_ingestion_service_handles_empty_source():
    adapter = FakeSourceAdapter(
        source_name="Empty Source",
        records=[],
    )

    events = IngestionService().ingest(adapter)

    assert events == []


def test_ingestion_service_sends_normalized_events_to_processor():
    adapter = FakeSourceAdapter(
        source_name="Test Source",
        records=[
            SourceRecord(source="Test Source", headline="Player One update.", player="Player One"),
            SourceRecord(source="Test Source", headline="Player Two update.", player="Player Two"),
        ],
    )
    processed = []

    events = IngestionService(event_processor=processed.append).ingest(adapter)

    assert processed == events
    assert [event.player for event in processed] == ["Player One", "Player Two"]


def test_ingestion_processor_failure_is_fail_open_and_does_not_refetch_provider():
    adapter = FakeSourceAdapter(
        source_name="Test Source",
        records=[SourceRecord(source="Test Source", headline="Player update.", player="Player One")],
    )

    def unavailable_processor(event):
        raise RuntimeError("Cortex unavailable")

    result = IngestionService(
        event_processor=unavailable_processor,
        max_attempts=3,
        backoff_seconds=0,
    ).ingest_result(adapter)

    assert result.success is True
    assert result.event_count == 1
    assert adapter.fetch_calls == 1
