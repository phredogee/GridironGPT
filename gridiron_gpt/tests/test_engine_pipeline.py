from uuid import uuid4

from gridiron_cortex.models.raw_event import RawEvent


def test_engine_pipeline_produces_prediction(tmp_path):
    engine = build_cortex_engine(tmp_path)

    sample_event = build_event(
        player="CJ Stroud",
        team="HOU",
        source="relationship_test",
        headline=(
            "CJ Stroud returns to practice and looks sharp with the "
            f"first-team offense. Test event {uuid4()}"
        ),
    )

    result = engine.process_event(sample_event)

    assert result.explanation != "Duplicate event ignored."
    assert result.predictions
    assert result.predictions[0].entity_id
    assert result.predictions[0].projected_trend in {
        "RISING",
        "STABLE",
        "FALLING",
    }
    assert 0.55 <= result.predictions[0].confidence <= 0.90
    assert result.recommendations

    recommendation = result.recommendations[0]

    assert any(
        "forecast:" in reason
        for reason in recommendation.reasons
    )

    assert result.evidence_chains

    chain = result.evidence_chains[0]

    assert chain.entity_name
    assert chain.steps
    assert chain.steps[0].faculty == "Observe"
    assert chain.steps[-1].faculty == "Decide"

    assert result.evidence_graphs

    graph = result.evidence_graphs[0]

    assert graph.get_roots()
    assert graph.get_terminals()
    assert graph.get_roots()[0].faculty == "Observe"
    assert graph.get_terminals()[0].faculty == "Decide"

from tests.builders.cortex_engine_builder import (
    build_cortex_engine,
)
from tests.builders.event_builder import (
    build_event,
)
