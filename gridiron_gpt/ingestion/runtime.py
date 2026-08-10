from __future__ import annotations

from typing import Protocol

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService


class CortexEventProcessor(Protocol):
    def process_event(self, event: RawEvent) -> object:
        ...


def build_runtime_ingestion_service(
    cortex: CortexEventProcessor,
    *,
    run_repository: JsonlIngestionRunRepository | None = None,
) -> IngestionService:
    """Compose the production ingestion service with Cortex processing enabled.

    This keeps application wiring in one place: providers and normalizers remain
    unaware of Cortex, while every normalized RawEvent is automatically handed to
    the same Cortex instance used by the running application.
    """
    return IngestionService(
        event_processor=cortex.process_event,
        run_repository=run_repository or JsonlIngestionRunRepository(),
    )
