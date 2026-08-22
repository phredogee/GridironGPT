from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from gridiron_gpt.ingestion.models.provider_health import ProviderHealthStatus


@dataclass(frozen=True)
class ProviderDiagnostic:
    source_name: str
    success: bool
    status: ProviderHealthStatus
    attempts: int
    records_received: int
    events_created: int
    error_type: str | None = None
    error_message: str | None = None
    cortex_events_accepted: int = 0
    cortex_duplicates_ignored: int = 0
    processor_failures: int = 0


@dataclass(frozen=True)
class IngestionRunSummary:
    run_id: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    providers_attempted: int
    providers_successful: int
    providers_failed: int
    records_received: int
    events_created: int
    diagnostics: list[ProviderDiagnostic] = field(default_factory=list)
    cortex_events_accepted: int = 0
    cortex_duplicates_ignored: int = 0
    processor_failures: int = 0

    @property
    def success(self) -> bool:
        return self.providers_failed == 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["started_at"] = self.started_at.isoformat()
        payload["completed_at"] = self.completed_at.isoformat()
        for diagnostic in payload["diagnostics"]:
            status = diagnostic["status"]
            diagnostic["status"] = status.value if hasattr(status, "value") else status
        payload["success"] = self.success
        return payload
