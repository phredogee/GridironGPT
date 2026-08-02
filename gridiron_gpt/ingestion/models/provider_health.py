from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProviderHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ProviderHealth:
    source_name: str
    status: ProviderHealthStatus
    consecutive_failures: int = 0
    total_successes: int = 0
    total_failures: int = 0
    last_success: datetime | None = None
    last_failure: datetime | None = None
    last_error_type: str | None = None
    last_error_message: str | None = None
    last_attempts: int = 0
    last_records_received: int = 0
    last_event_count: int = 0
