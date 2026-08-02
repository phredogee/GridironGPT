from datetime import datetime, timezone

from gridiron_gpt.ingestion.models.provider_health import ProviderHealthStatus
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class Adapter(SourceAdapter):
    def __init__(self, name, records=None, error=None):
        self.name = name
        self.records = records or []
        self.error = error

    @property
    def source_name(self):
        return self.name

    def fetch(self):
        if self.error:
            raise self.error
        return [SourceRecord(source=self.name, headline=headline) for headline in self.records]


def test_run_summary_aggregates_provider_metrics():
    ticks = iter([10.0, 12.5])
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None, monotonic=lambda: next(ticks))
    summary = service.ingest_run([
        Adapter("ESPN", ["one", "two"]),
        Adapter("RotoWire", ["three"]),
    ])

    assert summary.providers_attempted == 2
    assert summary.providers_successful == 2
    assert summary.providers_failed == 0
    assert summary.records_received == 3
    assert summary.events_created == 3
    assert summary.duration_seconds == 2.5
    assert summary.success is True


def test_provider_diagnostics_include_health_and_errors():
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None)
    summary = service.ingest_run([
        Adapter("ESPN", ["ok"]),
        Adapter("RotoWire", error=ConnectionError("offline")),
    ])
    diagnostics = {item.source_name: item for item in summary.diagnostics}

    assert diagnostics["ESPN"].status == ProviderHealthStatus.HEALTHY
    assert diagnostics["ESPN"].events_created == 1
    assert diagnostics["RotoWire"].status == ProviderHealthStatus.DEGRADED
    assert diagnostics["RotoWire"].error_type == "ConnectionError"
    assert diagnostics["RotoWire"].error_message == "offline"


def test_run_history_is_persisted_as_jsonl(tmp_path):
    repository = JsonlIngestionRunRepository(tmp_path / "runs.jsonl")
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=None,
        run_repository=repository,
    )
    summary = service.ingest_run([Adapter("ESPN", ["one"])])

    rows = repository.load_all()
    assert len(rows) == 1
    assert rows[0]["run_id"] == summary.run_id
    assert rows[0]["providers_successful"] == 1
    assert rows[0]["diagnostics"][0]["status"] == "healthy"
    assert repository.latest()["run_id"] == summary.run_id


def test_run_history_preserves_multiple_runs(tmp_path):
    repository = JsonlIngestionRunRepository(tmp_path / "runs.jsonl")
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None, run_repository=repository)
    first = service.ingest_run([Adapter("ESPN", ["one"])])
    second = service.ingest_run([Adapter("ESPN", ["two"])])

    rows = repository.load_all()
    assert [row["run_id"] for row in rows] == [first.run_id, second.run_id]
    assert repository.latest()["run_id"] == second.run_id


def test_empty_run_is_valid_and_observable():
    service = IngestionService(max_attempts=1, attempt_timeout_seconds=None)
    summary = service.ingest_run([])

    assert summary.providers_attempted == 0
    assert summary.providers_successful == 0
    assert summary.providers_failed == 0
    assert summary.records_received == 0
    assert summary.events_created == 0
    assert summary.diagnostics == []
    assert summary.success is True


def test_serialized_summary_contains_timestamps_and_success():
    moments = iter([
        datetime(2026, 8, 2, 18, 0, tzinfo=timezone.utc),
        datetime(2026, 8, 2, 18, 0, 1, tzinfo=timezone.utc),
    ])
    service = IngestionService(
        max_attempts=1,
        attempt_timeout_seconds=None,
        clock=lambda: next(moments),
    )
    payload = service.ingest_run([Adapter("ESPN", ["one"])]).to_dict()

    assert payload["started_at"].startswith("2026-08-02T18:00:00")
    assert payload["completed_at"].startswith("2026-08-02T18:00:01")
    assert payload["success"] is True
