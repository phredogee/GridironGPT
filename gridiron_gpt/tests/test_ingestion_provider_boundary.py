from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class HealthyAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Healthy Source"

    def fetch(self) -> list[SourceRecord]:
        return [
            SourceRecord(
                source=self.source_name,
                headline="Healthy Player update",
                player="Healthy Player",
            )
        ]


class FailingAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Failing Source"

    def fetch(self) -> list[SourceRecord]:
        raise RuntimeError("provider unavailable")


class EmptyAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Empty Source"

    def fetch(self) -> list[SourceRecord]:
        return []


def test_ingest_result_reports_success():
    result = IngestionService().ingest_result(HealthyAdapter())

    assert result.success is True
    assert result.source_name == "Healthy Source"
    assert result.records_received == 1
    assert result.event_count == 1
    assert result.error_type is None
    assert result.error_message is None


def test_ingest_result_reports_provider_failure_without_raising():
    result = IngestionService().ingest_result(FailingAdapter())

    assert result.success is False
    assert result.source_name == "Failing Source"
    assert result.events == []
    assert result.records_received == 0
    assert result.error_type == "RuntimeError"
    assert result.error_message == "provider unavailable"


def test_ingest_many_isolates_failing_provider():
    service = IngestionService()

    events = service.ingest_many(
        [FailingAdapter(), HealthyAdapter()]
    )

    assert len(events) == 1
    assert events[0].source == "Healthy Source"


def test_ingest_many_results_preserves_all_provider_outcomes():
    results = IngestionService().ingest_many_results(
        [HealthyAdapter(), FailingAdapter(), EmptyAdapter()]
    )

    assert len(results) == 3
    assert [result.source_name for result in results] == [
        "Healthy Source",
        "Failing Source",
        "Empty Source",
    ]
    assert [result.success for result in results] == [
        True,
        False,
        True,
    ]
    assert results[2].records_received == 0
    assert results[2].event_count == 0


def test_legacy_ingest_api_returns_empty_events_for_failure():
    events = IngestionService().ingest(FailingAdapter())

    assert events == []
