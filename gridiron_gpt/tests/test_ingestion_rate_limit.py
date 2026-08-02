import pytest

from gridiron_gpt.ingestion.models.provider_errors import ProviderRateLimitError
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class RateLimitedAdapter(SourceAdapter):
    def __init__(self, *, retry_after=None, recover_on_call=None):
        self.retry_after = retry_after
        self.recover_on_call = recover_on_call
        self.calls = 0

    @property
    def source_name(self) -> str:
        return "Rate Limited Source"

    def fetch(self):
        self.calls += 1
        if self.recover_on_call is not None and self.calls >= self.recover_on_call:
            return [SourceRecord(source=self.source_name, headline="Recovered")]
        raise ProviderRateLimitError(
            "HTTP 429 Too Many Requests",
            retry_after_seconds=self.retry_after,
        )


def test_retry_after_overrides_exponential_backoff():
    sleeps = []
    service = IngestionService(
        max_attempts=2,
        backoff_seconds=0.5,
        attempt_timeout_seconds=None,
        sleep=sleeps.append,
    )

    result = service.ingest_result(
        RateLimitedAdapter(retry_after=7.0, recover_on_call=2)
    )

    assert result.success is True
    assert result.attempts == 2
    assert sleeps == [7.0]


def test_rate_limit_without_retry_after_uses_normal_backoff():
    sleeps = []
    service = IngestionService(
        max_attempts=2,
        backoff_seconds=0.75,
        attempt_timeout_seconds=None,
        sleep=sleeps.append,
    )

    result = service.ingest_result(
        RateLimitedAdapter(retry_after=None, recover_on_call=2)
    )

    assert result.success is True
    assert sleeps == [0.75]


def test_exhausted_rate_limit_is_structured_failure():
    service = IngestionService(
        max_attempts=2,
        attempt_timeout_seconds=None,
        sleep=lambda _delay: None,
    )

    result = service.ingest_result(RateLimitedAdapter(retry_after=1.0))

    assert result.success is False
    assert result.attempts == 2
    assert result.error_type == "ProviderRateLimitError"
    assert result.error_message == "HTTP 429 Too Many Requests"


def test_rate_limited_provider_remains_isolated():
    class HealthyAdapter(SourceAdapter):
        @property
        def source_name(self):
            return "Healthy"

        def fetch(self):
            return [SourceRecord(source=self.source_name, headline="Healthy")]

    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=None,
        sleep=lambda _delay: None,
    )
    results = service.ingest_many_results(
        [RateLimitedAdapter(retry_after=1.0), HealthyAdapter()]
    )

    assert results[0].success is False
    assert results[0].error_type == "ProviderRateLimitError"
    assert results[1].success is True


def test_negative_retry_after_is_rejected():
    with pytest.raises(ValueError, match="retry_after_seconds"):
        ProviderRateLimitError(retry_after_seconds=-1)
