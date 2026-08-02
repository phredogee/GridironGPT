from gridiron_gpt.ingestion.models.provider_health import ProviderHealthStatus
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.services.provider_health_tracker import ProviderHealthTracker
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class SequencedAdapter(SourceAdapter):
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)

    @property
    def source_name(self):
        return "Sequenced Source"

    def fetch(self):
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return [SourceRecord(source=self.source_name, headline=outcome)]


def test_ingestion_service_records_success_health():
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None)
    result = service.ingest_result(SequencedAdapter(["event"]))
    health = service.health_tracker.get("Sequenced Source")

    assert result.success is True
    assert health is not None
    assert health.status == ProviderHealthStatus.HEALTHY
    assert health.last_event_count == 1


def test_ingestion_service_records_failure_health():
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None)
    result = service.ingest_result(SequencedAdapter([ConnectionError("offline")]))
    health = service.health_tracker.get("Sequenced Source")

    assert result.success is False
    assert health is not None
    assert health.status == ProviderHealthStatus.DEGRADED
    assert health.last_error_type == "ConnectionError"


def test_retried_success_is_recorded_as_degraded():
    service = IngestionService(
        max_attempts=2,
        backoff_seconds=0,
        attempt_timeout_seconds=None,
        sleep=lambda _delay: None,
    )
    result = service.ingest_result(SequencedAdapter([ConnectionError("temporary"), "recovered"]))
    health = service.health_tracker.get("Sequenced Source")

    assert result.success is True
    assert result.attempts == 2
    assert health.status == ProviderHealthStatus.DEGRADED
    assert health.last_attempts == 2


def test_custom_health_tracker_threshold_is_honored():
    health_tracker = ProviderHealthTracker(unavailable_after_failures=2)
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=None,
        health_tracker=health_tracker,
    )
    adapter = SequencedAdapter([ConnectionError("one"), ConnectionError("two")])

    service.ingest_result(adapter)
    service.ingest_result(adapter)

    assert health_tracker.get("Sequenced Source").status == ProviderHealthStatus.UNAVAILABLE
