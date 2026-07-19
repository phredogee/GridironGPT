from uuid import uuid4

from gridiron_cortex.engine.cortex_engine import CortexEngine
from gridiron_cortex.engine.entity_resolver import EntityResolver
from gridiron_cortex.engine.signal_processor import SignalProcessor
from gridiron_cortex.engine.relationship_engine import RelationshipEngine
from gridiron_cortex.engine.score_engine import ScoreEngine
from gridiron_cortex.engine.recommendation_engine import RecommendationEngine
from gridiron_cortex.engine.explanation_engine import ExplanationEngine
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.predict.prediction_engine import PredictionEngine
from gridiron_cortex.storage.json_event_repository import JsonEventRepository
from gridiron_cortex.storage.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_cortex.storage.json_relationship_repository import (
    JsonRelationshipRepository,
)

def test_engine_pipeline_produces_prediction(tmp_path):
    event_repository = JsonEventRepository(
        tmp_path / "events.jsonl"
    )
    scorecard_repository = JsonPlayerScorecardRepository(
        tmp_path / "scorecards.jsonl"
    )
    relationship_repository = JsonRelationshipRepository(
        tmp_path / "relationships.json"
    )

    engine = CortexEngine(
        entity_resolver=EntityResolver(),
        signal_processor=SignalProcessor(),
        relationship_engine=RelationshipEngine(
            repository=relationship_repository,
        ),
        score_engine=ScoreEngine(
            repository=scorecard_repository,
        ),
        recommendation_engine=RecommendationEngine(),
        explanation_engine=ExplanationEngine(),
        event_repository=event_repository,
        prediction_engine=PredictionEngine(),
    )

    sample_event = RawEvent(
        headline=(
            "CJ Stroud returns to practice and looks sharp with the "
            f"first-team offense. Test event {uuid4()}"
        ),
        source="relationship_test",
        player="CJ Stroud",
        team="HOU",
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
