from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.models.provider_errors import ProviderRateLimitError
from gridiron_gpt.ingestion.models.provider_ingestion_result import ProviderIngestionResult
from gridiron_gpt.ingestion.normalize.event_normalizer import EventNormalizer
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class ProviderTimeoutError(TimeoutError):
    """Raised when a provider fetch exceeds the configured attempt timeout."""


class IngestionService:
    """Coordinate resilient source retrieval and event normalization."""

    def __init__(
        self,
        normalizer: EventNormalizer | None = None,
        *,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
        attempt_timeout_seconds: float | None = 15.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds cannot be negative")
        if attempt_timeout_seconds is not None and attempt_timeout_seconds <= 0:
            raise ValueError("attempt_timeout_seconds must be positive or None")

        self.normalizer = normalizer or EventNormalizer()
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.attempt_timeout_seconds = attempt_timeout_seconds
        self.sleep = sleep

    def _fetch_with_timeout(self, adapter: SourceAdapter):
        if self.attempt_timeout_seconds is None:
            return adapter.fetch()

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(adapter.fetch)
        try:
            return future.result(timeout=self.attempt_timeout_seconds)
        except FutureTimeoutError as exc:
            future.cancel()
            raise ProviderTimeoutError(
                f"{adapter.source_name} exceeded "
                f"{self.attempt_timeout_seconds}s attempt timeout"
            ) from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _retry_delay(self, error: Exception, attempt: int) -> float:
        if isinstance(error, ProviderRateLimitError):
            retry_after = error.retry_after_seconds
            if retry_after is not None:
                return retry_after
        return self.backoff_seconds * (2 ** (attempt - 1))

    def ingest_result(self, adapter: SourceAdapter) -> ProviderIngestionResult:
        source_name = adapter.source_name
        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                records = self._fetch_with_timeout(adapter)
                events = self.normalizer.normalize_many(records)
                return ProviderIngestionResult(
                    source_name=source_name,
                    success=True,
                    events=events,
                    records_received=len(records),
                    attempts=attempt,
                )
            except Exception as exc:
                last_error = exc
                if attempt < self.max_attempts:
                    self.sleep(self._retry_delay(exc, attempt))

        assert last_error is not None
        return ProviderIngestionResult(
            source_name=source_name,
            success=False,
            attempts=self.max_attempts,
            error_type=type(last_error).__name__,
            error_message=str(last_error),
        )

    def ingest(self, adapter: SourceAdapter) -> list[RawEvent]:
        """Compatibility API returning only normalized events."""
        return self.ingest_result(adapter).events

    def ingest_many_results(
        self,
        adapters: list[SourceAdapter],
    ) -> list[ProviderIngestionResult]:
        return [self.ingest_result(adapter) for adapter in adapters]

    def ingest_many(self, adapters: list[SourceAdapter]) -> list[RawEvent]:
        """Compatibility API returning events from successful providers."""
        events: list[RawEvent] = []
        for result in self.ingest_many_results(adapters):
            events.extend(result.events)
        return events
