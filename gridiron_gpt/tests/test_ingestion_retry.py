import pytest

from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class FlakyAdapter(SourceAdapter):
    def __init__(self, failures_before_success: int):
        self.failures_before_success = failures_before_success
        self.calls = 0

    @property
    def source_name(self) -> str:
        return "Flaky Source"

    def fetch(self):
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise ConnectionError(f"temporary failure {self.calls}")
        return [SourceRecord(source=self.source_name, headline="Recovered event")]


def test_provider_retries_then_succeeds():
    adapter = FlakyAdapter(failures_before_success=2)
    sleeps = []
    service = IngestionService(max_attempts=3, backoff_seconds=0.5, sleep=sleeps.append)

    result = service.ingest_result(adapter)

    assert result.success is True
    assert result.attempts == 3
    assert result.event_count == 1
    assert adapter.calls == 3
    assert sleeps == [0.5, 1.0]


def test_provider_reports_failure_after_exhausting_retries():
    adapter = FlakyAdapter(failures_before_success=99)
    sleeps = []
    service = IngestionService(max_attempts=3, backoff_seconds=0.25, sleep=sleeps.append)

    result = service.ingest_result(adapter)

    assert result.success is False
    assert result.attempts == 3
    assert result.error_type == "ConnectionError"
    assert result.error_message == "temporary failure 3"
    assert sleeps == [0.25, 0.5]


def test_successful_provider_does_not_sleep_or_retry():
    adapter = FlakyAdapter(failures_before_success=0)
    sleeps = []
    result = IngestionService(sleep=sleeps.append).ingest_result(adapter)

    assert result.success is True
    assert result.attempts == 1
    assert adapter.calls == 1
    assert sleeps == []


def test_retry_policy_does_not_break_failure_isolation():
    failing = FlakyAdapter(failures_before_success=99)
    healthy = FlakyAdapter(failures_before_success=0)
    service = IngestionService(max_attempts=2, backoff_seconds=0, sleep=lambda _delay: None)

    results = service.ingest_many_results([failing, healthy])

    assert results[0].success is False
    assert results[0].attempts == 2
    assert results[1].success is True
    assert results[1].event_count == 1


def test_invalid_retry_configuration_is_rejected():
    with pytest.raises(ValueError, match="max_attempts"):
        IngestionService(max_attempts=0)
    with pytest.raises(ValueError, match="backoff_seconds"):
        IngestionService(backoff_seconds=-1)
