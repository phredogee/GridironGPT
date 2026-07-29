from pathlib import Path

from gridiron_cortex.engine.cortex_engine import CortexEngine
from gridiron_cortex.enrich.player_enrichment_service import (
    PlayerEnrichmentService,
)
from gridiron_cortex.evaluate.score_engine import ScoreEngine
from gridiron_cortex.explain.explanation_engine import (
    ExplanationEngine,
)
from gridiron_cortex.predict.prediction_engine import PredictionEngine
from gridiron_cortex.decide.recommendation_engine import (
    RecommendationEngine,
)
from gridiron_cortex.reason.relationship_engine import (
    RelationshipEngine,
)
from gridiron_cortex.reasoning.trend_analyzer import TrendAnalyzer
from gridiron_cortex.remember.json_event_repository import (
    JsonEventRepository,
)
from gridiron_cortex.remember.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_cortex.remember.json_relationship_repository import (
    JsonRelationshipRepository,
)
from gridiron_cortex.transforms.player_intelligence_builder import (
    PlayerIntelligenceBuilder,
)
from gridiron_cortex.transforms.player_snapshot_factory import (
    PlayerSnapshotFactory,
)
from gridiron_cortex.understand.entity_resolver import EntityResolver
from gridiron_cortex.understand.signal_processor import SignalProcessor


def build_cortex_engine(
    tmp_path: Path,
) -> CortexEngine:

    event_repository = JsonEventRepository(
        tmp_path / "events.jsonl"
    )

    scorecard_repository = (
        JsonPlayerScorecardRepository(
            tmp_path / "scorecards.jsonl"
        )
    )

    relationship_repository = (
        JsonRelationshipRepository(
            tmp_path / "relationships.jsonl"
        )
    )

    return CortexEngine(
        entity_resolver=EntityResolver(),
        player_enrichment=PlayerEnrichmentService(),
        signal_processor=SignalProcessor(),
        relationship_engine=RelationshipEngine(
            repository=relationship_repository,
        ),
        score_engine=ScoreEngine(
            repository=scorecard_repository,
        ),
        recommendation_engine=RecommendationEngine(),
        explanation_engine=ExplanationEngine(),
        player_snapshot_factory=PlayerSnapshotFactory(),
        player_intelligence_builder=PlayerIntelligenceBuilder(),
        trend_analyzer=TrendAnalyzer(),
        event_repository=event_repository,
        prediction_engine=PredictionEngine(),
    )
