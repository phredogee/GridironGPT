from __future__ import annotations

from typing import Protocol

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.services.ingestion_run_repository_factory import (
    build_ingestion_run_repository,
)
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService


class CortexEventProcessor(Protocol):
    def process_event(self, event: RawEvent) -> object:
        ...


def build_runtime_ingestion_service(
    cortex: CortexEventProcessor,
    *,
    run_repository=None,
) -> IngestionService:
    """Compose the production ingestion service with Cortex processing enabled.

    Providers and normalizers remain unaware of Cortex. Ingestion-run persistence is
    selected centrally: JSONL by default for local development, or durable Supabase
    when GRIDIRON_INGESTION_RUN_PERSISTENCE=supabase is explicitly configured.
    """
    return IngestionService(
        event_processor=cortex.process_event,
        run_repository=run_repository or build_ingestion_run_repository(),
    )
