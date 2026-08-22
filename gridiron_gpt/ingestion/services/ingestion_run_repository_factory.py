from __future__ import annotations

import os
from typing import Any, Callable

from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.supabase_ingestion_run_repository import SupabaseIngestionRunRepository


PERSISTENCE_ENV = "GRIDIRON_INGESTION_RUN_PERSISTENCE"


def build_ingestion_run_repository(
    *,
    environ: dict[str, str] | None = None,
    supabase_client_factory: Callable[[], Any] | None = None,
):
    """Build the configured ingestion-run repository.

    Local development defaults to JSONL. Durable Supabase persistence must be
    selected explicitly so a production/scheduled job cannot silently fall back to
    ephemeral local storage because of a missing secret or typo.
    """
    env = os.environ if environ is None else environ
    mode = env.get(PERSISTENCE_ENV, "jsonl").strip().lower()

    if mode == "jsonl":
        return JsonlIngestionRunRepository()

    if mode == "supabase":
        if supabase_client_factory is None:
            from gridiron_gpt.storage.supabase_client import get_supabase_client

            supabase_client_factory = get_supabase_client
        return SupabaseIngestionRunRepository(supabase_client_factory())

    raise ValueError(
        f"Unsupported {PERSISTENCE_ENV}={mode!r}; expected 'jsonl' or 'supabase'."
    )
