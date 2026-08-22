from __future__ import annotations

from typing import Any


class SupabaseIngestionRunRepository:
    """Durable repository for Cortex ingestion-run summaries.

    The client is injected so this adapter stays independently testable and does not
    couple the ingestion domain to Supabase configuration at import time.
    """

    def __init__(self, client: Any, *, table_name: str = "cortex_ingestion_runs") -> None:
        self._client = client
        self._table_name = table_name

    def save(self, run: Any) -> None:
        payload = run.to_dict() if hasattr(run, "to_dict") else dict(run)
        self._client.table(self._table_name).upsert(payload, on_conflict="run_id").execute()

    def load_all(self) -> list[dict[str, Any]]:
        result = (
            self._client.table(self._table_name)
            .select("*")
            .order("completed_at", desc=True)
            .execute()
        )
        return list(result.data or [])
