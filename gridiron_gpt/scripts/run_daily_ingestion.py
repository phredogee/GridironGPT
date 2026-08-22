from __future__ import annotations

from pathlib import Path
import sys

# Support direct execution from the inner project root:
#   python scripts/run_daily_ingestion.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gridiron_gpt.ingestion.ingest import ingest_all


def main() -> int:
    """Run the production NFL-news ingestion path and print scheduler-friendly results."""
    summary = ingest_all()

    print("GridironGPT daily ingestion")
    print("=" * 27)
    print(f"run_id={summary.run_id}")
    print(f"started_at={summary.started_at.isoformat()}")
    print(f"completed_at={summary.completed_at.isoformat()}")
    print(f"duration_seconds={summary.duration_seconds:.3f}")
    print(f"providers_attempted={summary.providers_attempted}")
    print(f"providers_successful={summary.providers_successful}")
    print(f"providers_failed={summary.providers_failed}")
    print(f"records_received={summary.records_received}")
    print(f"events_created={summary.events_created}")
    print(f"cortex_events_accepted={summary.cortex_events_accepted}")
    print(f"cortex_duplicates_ignored={summary.cortex_duplicates_ignored}")
    print(f"processor_failures={summary.processor_failures}")

    for diagnostic in summary.diagnostics:
        print(
            "provider="
            f"{diagnostic.source_name} "
            f"success={diagnostic.success} "
            f"records={diagnostic.records_received} "
            f"events={diagnostic.events_created} "
            f"cortex_new={diagnostic.cortex_events_accepted} "
            f"duplicates={diagnostic.cortex_duplicates_ignored} "
            f"processor_failures={diagnostic.processor_failures}"
        )

    if summary.providers_failed or summary.processor_failures:
        print("status=attention")
        return 1

    print("status=healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
