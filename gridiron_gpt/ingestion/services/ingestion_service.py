from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timezone

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.models.ingestion_run import IngestionRunSummary, ProviderDiagnostic
from gridiron_gpt.ingestion.models.provider_errors import ProviderRateLimitError
from gridiron_gpt.ingestion.models.provider_health import ProviderHealthStatus
from gridiron_gpt.ingestion.models.provider_ingestion_result import ProviderIngestionResult
from gridiron_gpt.ingestion.normalize.event_normalizer import EventNormalizer
from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.provider_health_tracker import ProviderHealthTracker
from gridiron_gpt.ingestion.sources.base import SourceAdapter

logger = logging.getLogger(__name__)


class ProviderTimeoutError(TimeoutError):
    """Raised when a provider fetch exceeds the configured attempt timeout."""


class IngestionService:
    """Coordinate resilient source retrieval, normalization, health, and observability.

    An optional event processor can be injected to consume every normalized RawEvent.
    This is the integration boundary for Cortex. Processor failures are fail-open so a
    downstream intelligence outage never turns a successful provider fetch into an
    ingestion failure or causes the provider to be fetched again.
    """

    def __init__(
        self,
        normalizer: EventNormalizer | None = None,
        *,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
        attempt_timeout_seconds: float | None = 15.0,
        sleep: Callable[[float], None] = time.sleep,
        health_tracker: ProviderHealthTracker | None = None,
        run_repository: JsonlIngestionRunRepository | None = None,
        event_processor: Callable[[RawEvent], object] | None = None,
        clock: Callable[[], datetime] | None = None,
        monotonic: Callable[[], float] = time.monotonic,
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
        self.health_tracker = health_tracker or ProviderHealthTracker()
        self.run_repository = run_repository
        self.event_processor = event_processor
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.monotonic = monotonic

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
                f"{adapter.source_name} exceeded {self.attempt_timeout_seconds}s attempt timeout"
            ) from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _retry_delay(self, error: Exception, attempt: int) -> float:
        if isinstance(error, ProviderRateLimitError) and error.retry_after_seconds is not None:
            return error.retry_after_seconds
        return self.backoff_seconds * (2 ** (attempt - 1))

    def _record_result(self, result: ProviderIngestionResult) -> ProviderIngestionResult:
        self.health_tracker.record(result)
        return result

    def _process_events(self, events: list[RawEvent]) -> tuple[int, int, int]:
        if self.event_processor is None:
            return 0, 0, 0

        accepted = 0
        duplicates = 0
        failures = 0
        for event in events:
            try:
                result = self.event_processor(event)
                explanation = getattr(result, "explanation", None)
                if explanation == "Duplicate event ignored.":
                    duplicates += 1
                else:
                    accepted += 1
            except Exception:
                failures += 1
                source_id = event.evidence.get("source_id") if event.evidence else None
                logger.exception(
                    "Downstream event processor failed for source=%s source_id=%s; ingestion remains successful",
                    event.source,
                    source_id,
                )
        return accepted, duplicates, failures

    def ingest_result(self, adapter: SourceAdapter) -> ProviderIngestionResult:
        source_name = adapter.source_name
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                records = self._fetch_with_timeout(adapter)
                events = self.normalizer.normalize_many(records)
            except Exception as exc:
                last_error = exc
                if attempt < self.max_attempts:
                    self.sleep(self._retry_delay(exc, attempt))
                continue

            accepted, duplicates, failures = self._process_events(events)
            return self._record_result(ProviderIngestionResult(
                source_name=source_name,
                success=True,
                events=events,
                records_received=len(records),
                attempts=attempt,
                cortex_events_accepted=accepted,
                cortex_duplicates_ignored=duplicates,
                processor_failures=failures,
            ))

        assert last_error is not None
        return self._record_result(ProviderIngestionResult(
            source_name=source_name, success=False, attempts=self.max_attempts,
            error_type=type(last_error).__name__, error_message=str(last_error),
        ))

    def _diagnostic(self, result: ProviderIngestionResult) -> ProviderDiagnostic:
        health = self.health_tracker.get(result.source_name)
        status = health.status if health else (
            ProviderHealthStatus.HEALTHY if result.success else ProviderHealthStatus.DEGRADED
        )
        return ProviderDiagnostic(
            source_name=result.source_name,
            success=result.success,
            status=status,
            attempts=result.attempts,
            records_received=result.records_received,
            events_created=result.event_count,
            error_type=result.error_type,
            error_message=result.error_message,
            cortex_events_accepted=result.cortex_events_accepted,
            cortex_duplicates_ignored=result.cortex_duplicates_ignored,
            processor_failures=result.processor_failures,
        )

    def ingest_run(self, adapters: list[SourceAdapter]) -> IngestionRunSummary:
        """Execute a complete observable ingestion run and optionally persist it."""
        started_at = self.clock()
        started_tick = self.monotonic()
        results = self.ingest_many_results(adapters)
        completed_at = self.clock()
        duration = max(0.0, self.monotonic() - started_tick)
        summary = IngestionRunSummary(
            run_id=str(uuid.uuid4()),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=round(duration, 6),
            providers_attempted=len(results),
            providers_successful=sum(1 for result in results if result.success),
            providers_failed=sum(1 for result in results if not result.success),
            records_received=sum(result.records_received for result in results),
            events_created=sum(result.event_count for result in results),
            diagnostics=[self._diagnostic(result) for result in results],
            cortex_events_accepted=sum(result.cortex_events_accepted for result in results),
            cortex_duplicates_ignored=sum(result.cortex_duplicates_ignored for result in results),
            processor_failures=sum(result.processor_failures for result in results),
        )
        if self.run_repository is not None:
            self.run_repository.save(summary)
        return summary

    def ingest(self, adapter: SourceAdapter) -> list[RawEvent]:
        return self.ingest_result(adapter).events

    def ingest_many_results(self, adapters: list[SourceAdapter]) -> list[ProviderIngestionResult]:
        return [self.ingest_result(adapter) for adapter in adapters]

    def ingest_many(self, adapters: list[SourceAdapter]) -> list[RawEvent]:
        events: list[RawEvent] = []
        for result in self.ingest_many_results(adapters):
            events.extend(result.events)
        return events
