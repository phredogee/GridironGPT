from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class IngestionFreshness:
    """Presentation-safe freshness state derived from persisted ingestion runs."""

    status: str
    label: str
    completed_at: datetime | None
    age: timedelta | None
    run_success: bool | None

    @property
    def is_fresh(self) -> bool:
        return self.status == "fresh"


def _as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluate_ingestion_freshness(
    runs: Iterable[dict[str, Any]],
    *,
    now: datetime | None = None,
    fresh_for: timedelta = timedelta(hours=26),
) -> IngestionFreshness:
    """Evaluate the latest persisted run without coupling Streamlit to storage details.

    A 26-hour default allows a daily job modest scheduling/runtime drift while still
    making a missed day visible. A failed latest run is always attention-worthy even
    if it completed recently.
    """
    if fresh_for <= timedelta(0):
        raise ValueError("fresh_for must be positive")

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    latest: dict[str, Any] | None = None
    latest_completed: datetime | None = None
    for run in runs:
        completed = _as_datetime(run.get("completed_at"))
        if completed is not None and (latest_completed is None or completed > latest_completed):
            latest = run
            latest_completed = completed

    if latest is None or latest_completed is None:
        return IngestionFreshness("missing", "No ingestion history", None, None, None)

    age = max(timedelta(0), now - latest_completed)
    success = bool(latest.get("success", False))
    if not success:
        return IngestionFreshness("failed", "Latest ingestion needs attention", latest_completed, age, False)
    if age <= fresh_for:
        return IngestionFreshness("fresh", "Updated today", latest_completed, age, True)
    return IngestionFreshness("stale", "Ingestion data is stale", latest_completed, age, True)
