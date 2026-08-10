from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.runtime import build_runtime_ingestion_service
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class FakeAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Runtime Source"

    def fetch(self) -> list[SourceRecord]:
        return [
            SourceRecord(
                source=self.source_name,
                headline="Tank Dell returns to full practice.",
                player="Tank Dell",
                team="HOU",
                position="WR",
            )
        ]


class FakeCortex:
    def __init__(self) -> None:
        self.events = []

    def process_event(self, event):
        self.events.append(event)
        return {"processed": True}


def test_runtime_ingestion_automatically_routes_events_to_cortex(tmp_path):
    from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository

    cortex = FakeCortex()
    repository = JsonlIngestionRunRepository(tmp_path / "runs.jsonl")
    ingestion = build_runtime_ingestion_service(cortex, run_repository=repository)

    events = ingestion.ingest(FakeAdapter())

    assert len(events) == 1
    assert cortex.events == events
    assert cortex.events[0].player == "Tank Dell"


def test_runtime_ingestion_keeps_run_repository_enabled(tmp_path):
    from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository

    cortex = FakeCortex()
    repository = JsonlIngestionRunRepository(tmp_path / "runs.jsonl")
    ingestion = build_runtime_ingestion_service(cortex, run_repository=repository)

    summary = ingestion.ingest_run([FakeAdapter()])

    assert summary.success is True
    assert summary.events_created == 1
    assert repository.latest() is not None
    assert len(cortex.events) == 1
