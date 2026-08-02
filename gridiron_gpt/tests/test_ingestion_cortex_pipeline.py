from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.services.ingestion_service import (
    IngestionService,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class FakeRSSAdapter(SourceAdapter):

    @property
    def source_name(self) -> str:
        return "Test RSS"

    def fetch(self) -> list[SourceRecord]:
        return [
            SourceRecord(
                source=self.source_name,
                headline=(
                    "Tank Dell returns as a full participant "
                    "in practice."
                ),
                summary=(
                    "Dell returned to practice and participated "
                    "fully with Houston."
                ),
                player="Tank Dell",
                team="HOU",
                position="WR",
                published_at="2026-08-01T12:00:00Z",
                url="https://example.com/tank-dell",
                source_id="rss-story-123",
            )
        ]


def test_ingestion_pipeline_reaches_cortex(
    tmp_path: Path,
):
    ingestion = IngestionService()
    adapter = FakeRSSAdapter()

    events = ingestion.ingest(adapter)

    assert len(events) == 1

    event = events[0]

    # Ingestion supplies evidence, not conclusions.
    assert event.player == "Tank Dell"
    assert event.team == "HOU"
    assert event.position == "WR"
    assert event.sentiment is None
    assert event.impact_score is None
    assert event.confidence is None

    cortex = CortexFacade(
        data_directory=tmp_path,
    )

    result = cortex.process_event(event)

    # Cortex performs interpretation.
    assert result.signal is not None
    assert result.signal.impact_score > 0
    assert result.signal.sentiment == "positive"

    # The event reaches Cortex scoring.
    assert result.player_scorecards

    scorecard = next(
        scorecard
        for scorecard in result.player_scorecards
        if scorecard.player_name == "Tank Dell"
    )

    assert scorecard.overall_score > 50.0
    assert scorecard.health_score > 50.0

    # Cortex reaches its decision/explanation layers.
    assert result.recommendations
    assert result.evidence_chains
