from datetime import UTC, datetime
from pathlib import Path

from gridiron_gpt.ingestion.models.ingestion_run import IngestionRunSummary
from gridiron_gpt.ingestion.scheduled_runner import IngestionRunLock, run_scheduled_ingestion_once


def _summary(*, providers_failed: int = 0) -> IngestionRunSummary:
    now = datetime.now(UTC)
    return IngestionRunSummary(
        run_id="run-test",
        started_at=now,
        completed_at=now,
        duration_seconds=0.1,
        providers_attempted=2,
        providers_successful=2 - providers_failed,
        providers_failed=providers_failed,
        records_received=4,
        events_created=3,
        diagnostics=[],
    )


def test_scheduled_runner_returns_success_and_releases_lock(tmp_path: Path):
    lock_path = tmp_path / "scheduled.lock"
    result = run_scheduled_ingestion_once(
        lock_path=lock_path,
        ingest=lambda: _summary(),
    )

    assert result.status == "success"
    assert result.exit_code == 0
    assert result.summary is not None
    assert not lock_path.exists()


def test_scheduled_runner_reports_provider_failure(tmp_path: Path):
    result = run_scheduled_ingestion_once(
        lock_path=tmp_path / "scheduled.lock",
        ingest=lambda: _summary(providers_failed=1),
    )

    assert result.status == "provider_failure"
    assert result.exit_code == 1


def test_scheduled_runner_skips_when_another_run_holds_lock(tmp_path: Path):
    lock_path = tmp_path / "scheduled.lock"
    lock = IngestionRunLock(lock_path)
    assert lock.acquire()
    called = False

    def ingest():
        nonlocal called
        called = True
        return _summary()

    try:
        result = run_scheduled_ingestion_once(lock_path=lock_path, ingest=ingest)
    finally:
        lock.release()

    assert result.status == "already_running"
    assert result.exit_code == 0
    assert not called


def test_scheduled_runner_releases_lock_after_unexpected_failure(tmp_path: Path):
    lock_path = tmp_path / "scheduled.lock"

    def explode():
        raise RuntimeError("boom")

    result = run_scheduled_ingestion_once(lock_path=lock_path, ingest=explode)

    assert result.status == "runner_failure"
    assert result.exit_code == 2
    assert not lock_path.exists()
