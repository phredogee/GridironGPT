from datetime import datetime, timezone
from typing import Optional

from gridiron_gpt.storage.supabase_client import get_supabase_client


def start_ingestion_run(source: str) -> int:
    client = get_supabase_client()

    result = (
        client.table("ingestion_runs")
        .insert(
            {
                "source": source,
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .execute()
    )

    return result.data[0]["id"]


def finish_ingestion_run(
    run_id: int,
    status: str,
    articles_found: int = 0,
    articles_new: int = 0,
    articles_skipped: int = 0,
    error_message: Optional[str] = None,
) -> None:
    client = get_supabase_client()

    client.table("ingestion_runs").update(
        {
            "status": status,
            "articles_found": articles_found,
            "articles_new": articles_new,
            "articles_skipped": articles_skipped,
            "error_message": error_message,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", run_id).execute()
