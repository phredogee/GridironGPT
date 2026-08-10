from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.replay.replay_engine import ReplayEngine
from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.runtime import build_runtime_ingestion_service
from gridiron_gpt.ingestion.services.ingestion_run_repository import JsonlIngestionRunRepository
from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.base import SourceAdapter


class FakeRSSAdapter(SourceAdapter):
    @property
    def source_name(self) -> str:
        return "Test RSS"

    def fetch(self) -> list[SourceRecord]:
        return [SourceRecord(source=self.source_name, headline="Tank Dell returns as a full participant in practice.", summary="Dell returned to practice and participated fully with Houston.", player="Tank Dell", team="HOU", position="WR", published_at="2026-08-01T12:00:00Z", url="https://example.com/tank-dell", source_id="rss-story-123")]


def test_ingestion_pipeline_automatically_reaches_cortex(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path); processed_results = []
    def process_event(event):
        result = cortex.process_event(event); processed_results.append(result); return result
    ingestion = IngestionService(event_processor=process_event); events = ingestion.ingest(FakeRSSAdapter())
    assert len(events) == 1; assert len(processed_results) == 1
    event = events[0]
    assert event.player == "Tank Dell"; assert event.team == "HOU"; assert event.position == "WR"; assert event.sentiment is None; assert event.impact_score is None; assert event.confidence is None
    result = processed_results[0]
    assert result.signal is not None; assert result.signal.impact_score > 0; assert result.signal.sentiment == "positive"; assert result.player_scorecards
    scorecard = next(scorecard for scorecard in result.player_scorecards if scorecard.player_name == "Tank Dell")
    assert scorecard.overall_score > 50.0; assert scorecard.health_score > 50.0; assert result.recommendations; assert result.evidence_chains


def test_runtime_ingestion_persists_full_cortex_decision_for_replay(tmp_path: Path):
    """Production composition must survive a restart and remain replayable."""
    cortex_dir = tmp_path / "cortex"
    run_repo = JsonlIngestionRunRepository(tmp_path / "ingestion" / "runs.jsonl")
    cortex = CortexFacade(data_directory=cortex_dir)
    ingestion = build_runtime_ingestion_service(cortex, run_repository=run_repo)

    events = ingestion.ingest(FakeRSSAdapter())
    assert len(events) == 1
    correlation_id = events[0].fingerprint()

    # Live runtime exposes the published pipeline trail and persisted score state.
    live_history = cortex.get_event_history(correlation_id=correlation_id)
    assert live_history
    assert cortex.get_player_scorecard("Tank Dell") is not None

    # Simulate an application restart. The new facade must reload persisted event
    # bus history and Replay must reconstruct the same decision without reprocessing.
    restarted = CortexFacade(data_directory=cortex_dir)
    persisted_history = restarted.get_event_history(correlation_id=correlation_id)
    assert persisted_history
    assert len(persisted_history) == len(live_history)

    replay = ReplayEngine(restarted.event_bus).by_correlation(correlation_id)
    assert replay is not None
    assert replay.entity_name == "Tank Dell"
    assert replay.steps
    assert replay.recommendation is not None

    # Ingestion observability is persisted alongside Cortex state.
    latest_run = run_repo.latest()
    assert latest_run is not None
