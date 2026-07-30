from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAnalyzer,
)

def test_facade_processes_event(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline=(
            "Facade Test Player returns to practice "
            "with the first-team offense."
        ),
        source="facade_test",
        player="Facade Test Player",
        team="TST",
    )

    result = cortex.process_event(event)

    assert result.event == event
    assert result.signal is not None
    assert result.entities
    assert result.impacts
    assert result.score_updates
    assert result.player_scorecards
    assert result.recommendations


def test_facade_rejects_duplicate_event(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline="Duplicate Test Player returns to practice.",
        source="duplicate_test",
        player="Duplicate Test Player",
        team="TST",
    )

    first_result = cortex.process_event(event)
    second_result = cortex.process_event(event)

    assert first_result.signal is not None
    assert second_result.signal is None
    assert second_result.explanation == "Duplicate event ignored."


def test_facade_reads_player_scorecard(tmp_path: Path):
    cortex = CortexFacade(data_directory=tmp_path)

    event = RawEvent(
        headline="Scorecard Test Player returns to practice.",
        source="scorecard_test",
        player="Scorecard Test Player",
        team="TST",
    )

    cortex.process_event(event)

    scorecard = cortex.get_player_scorecard(
        "scorecard_test_player"
    )

    assert scorecard is not None
    assert scorecard.player_name == "Scorecard Test Player"
    assert abs(scorecard.overall_score - 50.9) < 0.000001
