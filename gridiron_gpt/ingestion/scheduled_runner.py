from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from gridiron_gpt.ingestion.ingest import ingest_all
from gridiron_gpt.ingestion.models.ingestion_run import IngestionRunSummary

logger = logging.getLogger(__name__)

DEFAULT_LOCK_PATH = Path("data/ingestion/scheduled_ingestion.lock")


@dataclass(frozen=True)
class ScheduledRunResult:
    status: str
    exit_code: int
    summary: IngestionRunSummary | None = None


class IngestionRunLock:
    """Process lock that prevents overlapping scheduled ingestion runs.

    The lock file stores the owning PID. If a previous process died without
    cleaning up, a later run detects the stale PID and safely recovers the lock.
    """

    def __init__(self, path: Path = DEFAULT_LOCK_PATH) -> None:
        self.path = path
        self._fd: int | None = None

    def _owner_pid(self) -> int | None:
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
            return int(raw)
        except (FileNotFoundError, ValueError, OSError):
            return None

    @staticmethod
    def _pid_is_running(pid: int | None) -> bool:
        if pid is None or pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        for _ in range(2):
            try:
                self._fd = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o644,
                )
            except FileExistsError:
                owner_pid = self._owner_pid()
                if self._pid_is_running(owner_pid):
                    return False
                logger.warning(
                    "Removing stale scheduled-ingestion lock %s owned by pid=%s",
                    self.path,
                    owner_pid,
                )
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass
                continue

            os.write(self._fd, f"{os.getpid()}\n".encode("utf-8"))
            return True

        return False

    def release(self) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self) -> "IngestionRunLock":
        if not self.acquire():
            raise RuntimeError("scheduled ingestion is already running")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()


def _summary_log_payload(summary: IngestionRunSummary) -> str:
    payload = {
        "run_id": summary.run_id,
        "success": summary.success,
        "providers_attempted": summary.providers_attempted,
        "providers_successful": summary.providers_successful,
        "providers_failed": summary.providers_failed,
        "records_received": summary.records_received,
        "events_created": summary.events_created,
        "duration_seconds": round(summary.duration_seconds, 3),
    }
    return json.dumps(payload, sort_keys=True)


def run_scheduled_ingestion_once(
    *,
    lock_path: Path = DEFAULT_LOCK_PATH,
    ingest: Callable[[], IngestionRunSummary] = ingest_all,
) -> ScheduledRunResult:
    """Run one scheduled ingestion cycle safely.

    Exit codes:
    - 0: completed successfully or skipped because another run owns the lock
    - 1: one or more providers failed
    - 2: unexpected runner failure
    """
    lock = IngestionRunLock(lock_path)
    if not lock.acquire():
        logger.warning("Scheduled ingestion skipped: another run owns %s", lock_path)
        return ScheduledRunResult(status="already_running", exit_code=0)

    try:
        summary = ingest()
        logger.info("Scheduled ingestion complete: %s", _summary_log_payload(summary))
        if summary.success:
            return ScheduledRunResult(status="success", exit_code=0, summary=summary)
        return ScheduledRunResult(status="provider_failure", exit_code=1, summary=summary)
    except Exception:
        logger.exception("Scheduled ingestion failed unexpectedly")
        return ScheduledRunResult(status="runner_failure", exit_code=2)
    finally:
        lock.release()
