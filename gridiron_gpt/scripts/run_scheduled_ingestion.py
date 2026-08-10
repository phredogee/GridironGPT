from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from gridiron_gpt.ingestion.scheduled_runner import (
    DEFAULT_LOCK_PATH,
    run_scheduled_ingestion_once,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one safe GridironGPT ingestion cycle through Cortex.",
    )
    parser.add_argument(
        "--lock-file",
        type=Path,
        default=DEFAULT_LOCK_PATH,
        help="Path used to prevent overlapping ingestion runs.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    result = run_scheduled_ingestion_once(lock_path=args.lock_file)
    if result.summary is not None:
        print(
            "ingestion_status="
            f"{result.status} run_id={result.summary.run_id} "
            f"events={result.summary.events_created} "
            f"providers_failed={result.summary.providers_failed}"
        )
    else:
        print(f"ingestion_status={result.status}")
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
