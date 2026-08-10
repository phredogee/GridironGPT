import time

import pytest

from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class SlowAdapter(SourceAdapter):
    def __init__(self, delay: float, *, recover_on_call: int | None = None):
        self.delay = delay
        self.recover_on_call = recover_on_call
        self.calls = 0

    @property
    def source_name(self) -> str:
        return "Slow Source"

    def fetch(self):
        self.calls += 1
        if self.recover_on_call is not None and self.calls >= self.recover_on_call:
            return [SourceRecord(source=self.source_name, headline="Recovered")]
        time.sleep(self.delay)
        return [SourceRecord(source=self.source_name, headline="Late event")]


class HealthyAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Healthy Source"

    def fetch(self):
        return [SourceRecord(source=self.source_name, headline="Healthy event")]


def test_provider_timeout_becomes_structured_failure():
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=0.01,
        sleep=lambda _delay: None,
    )

    result = service.ingest_result(SlowAdapter(0.1))

    assert result.success is False
    assert result.attempts == 1
    assert result.error_type == "ProviderTimeoutError"
    assert "exceeded 0.01s attempt timeout" in result.error_message


def test_timeout_participates_in_retry_policy():
    adapter = SlowAdapter(0.1, recover_on_call=2)
    sleeps = []
    service = IngestionService(
        max_attempts=2,
        backoff_seconds=0.25,
        attempt_timeout_seconds=0.01,
        sleep=sleeps.append,
    )

    result = service.ingest_result(adapter)

    assert result.success is True
    assert result.attempts == 2
    assert result.event_count == 1
    assert sleeps == [0.25]


def test_timed_out_provider_does_not_block_healthy_provider():
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=0.01,
        sleep=lambda _delay: None,
    )

    results = service.ingest_many_results([SlowAdapter(0.1), HealthyAdapter()])

    assert results[0].success is False
    assert results[0].error_type == "ProviderTimeoutError"
    assert results[1].success is True
    assert results[1].event_count == 1


def test_timeout_can_be_disabled():
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=None,
        sleep=lambda _delay: None,
    )

    result = service.ingest_result(SlowAdapter(0.001))

    assert result.success is True
    assert result.attempts == 1


def test_invalid_timeout_configuration_is_rejected():
    with pytest.raises(ValueError, match="attempt_timeout_seconds"):
        IngestionService(attempt_timeout_seconds=0)
    with pytest.raises(ValueError, match="attempt_timeout_seconds"):
        IngestionService(attempt_timeout_seconds=-1)
