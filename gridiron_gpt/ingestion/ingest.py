from __future__ import annotations

from gridiron_cortex.facade import CortexFacade
from gridiron_gpt.ingestion.models.ingestion_run import IngestionRunSummary
from gridiron_gpt.ingestion.runtime import build_runtime_ingestion_service
from gridiron_gpt.ingestion.sources.nfl_news import default_nfl_news_adapters


def ingest_all(cortex: CortexFacade | None = None) -> IngestionRunSummary:
    """Run the default GridironGPT news ingestion path through Cortex.

    A caller may provide the application's existing CortexFacade so ingestion,
    Replay, Mission Control, and persistence all observe the same engine instance.
    Standalone callers receive a fully configured facade automatically.
    """
    cortex = cortex or CortexFacade()
    ingestion = build_runtime_ingestion_service(cortex)
    return ingestion.ingest_run(default_nfl_news_adapters())
