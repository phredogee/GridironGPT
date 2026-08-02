from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from gridiron_gpt.ingestion.models.provider_health import (
    ProviderHealth,
    ProviderHealthStatus,
)
from gridiron_gpt.ingestion.models.provider_ingestion_result import ProviderIngestionResult


class ProviderHealthTracker:
    """Maintain process-local operational health for ingestion providers."""

    def __init__(
        self,
        *,
        unavailable_after_failures: int = 3,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if unavailable_after_failures < 1:
            raise ValueError("unavailable_after_failures must be at least 1")
        self.unavailable_after_failures = unavailable_after_failures
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._health: dict[str, ProviderHealth] = {}

    def record(self, result: ProviderIngestionResult) -> ProviderHealth:
        previous = self._health.get(result.source_name)
        now = self.clock()
        successes = previous.total_successes if previous else 0
        failures = previous.total_failures if previous else 0

        if result.success:
            successes += 1
            status = (
                ProviderHealthStatus.HEALTHY
                if result.attempts == 1
                else ProviderHealthStatus.DEGRADED
            )
            health = ProviderHealth(
                source_name=result.source_name,
                status=status,
                consecutive_failures=0,
                total_successes=successes,
                total_failures=failures,
                last_success=now,
                last_failure=previous.last_failure if previous else None,
                last_error_type=None,
                last_error_message=None,
                last_attempts=result.attempts,
                last_records_received=result.records_received,
                last_event_count=result.event_count,
            )
        else:
            failures += 1
            consecutive = (previous.consecutive_failures if previous else 0) + 1
            status = (
                ProviderHealthStatus.UNAVAILABLE
                if consecutive >= self.unavailable_after_failures
                else ProviderHealthStatus.DEGRADED
            )
            health = ProviderHealth(
                source_name=result.source_name,
                status=status,
                consecutive_failures=consecutive,
                total_successes=successes,
                total_failures=failures,
                last_success=previous.last_success if previous else None,
                last_failure=now,
                last_error_type=result.error_type,
                last_error_message=result.error_message,
                last_attempts=result.attempts,
                last_records_received=result.records_received,
                last_event_count=result.event_count,
            )

        self._health[result.source_name] = health
        return health

    def get(self, source_name: str) -> ProviderHealth | None:
        return self._health.get(source_name)

    def all(self) -> list[ProviderHealth]:
        return list(self._health.values())
