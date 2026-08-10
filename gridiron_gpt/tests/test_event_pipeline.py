from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.intake.event_pipeline import (
    process_rss_items,
)
from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAnalyzer,
)

def test_event_pipeline(tmp_path):

    cortex = CortexFacade(
        data_directory=tmp_path,
    )

    items = [
        {
            "headline": "Tank Dell returns to practice.",
            "source": "Test Feed",
            "player": "Tank Dell",
            "team": "HOU",
            "fantasy_impact": "positive",
            "date": "2026-07-13",
            "url": "https://example.com/story",
        }
    ]

    results = process_rss_items(
        items,
        cortex,
    )

    assert len(results) == 1

    assert (
        results[0].event.player
        == "Tank Dell"
    )
