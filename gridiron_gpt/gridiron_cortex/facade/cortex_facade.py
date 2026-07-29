from pathlib import Path

from gridiron_cortex.engine.cortex_engine import CortexEngine
from gridiron_cortex.understand.entity_resolver import EntityResolver
from gridiron_cortex.explain.explanation_engine import ExplanationEngine
from gridiron_cortex.decide.recommendation_engine import RecommendationEngine
from gridiron_cortex.reason.relationship_engine import RelationshipEngine
from gridiron_cortex.evaluate.score_engine import ScoreEngine
from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_cortex.knowledge.knowledge_service import KnowledgeService
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.predict.prediction_engine import PredictionEngine
from gridiron_cortex.remember.json_event_repository import JsonEventRepository
from gridiron_cortex.remember.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_cortex.remember.json_relationship_repository import (
    JsonRelationshipRepository,
)
from gridiron_cortex.transforms.player_snapshot_factory import (
    PlayerSnapshotFactory,
)
from gridiron_cortex.knowledge.knowledge_graph_manager import (
    KnowledgeGraphManager,
)
from gridiron_cortex.propagation.propagation_planner import (
    PropagationPlanner,
)
from gridiron_cortex.understand.evidence_aggregator import (
    EvidenceAggregator,
)
from gridiron_cortex.enrich.player_enrichment_service import (
    PlayerEnrichmentService,
)
from gridiron_cortex.reasoning.trend_analyzer import TrendAnalyzer
from gridiron_cortex.transforms.player_intelligence_builder import (
    PlayerIntelligenceBuilder,
)

class CortexFacade:
    """
    Public entry point for Gridiron Cortex.

    Applications should use this facade instead of constructing
    engine components or repositories directly.
    """

    def __init__(
        self,
        data_directory: str | Path = "data/cortex",
    ):
        data_path = Path(data_directory)

        event_repository = JsonEventRepository(
            data_path / "events.jsonl"
        )

        player_scorecard_repository = (
            JsonPlayerScorecardRepository(
                data_path / "player_scorecards.jsonl"
            )
        )

        evidence_aggregator = EvidenceAggregator()

        relationship_repository = JsonRelationshipRepository(
            data_path / "relationships.jsonl"
        )

        self.knowledge = KnowledgeService(
            event_repository=event_repository,
            player_scorecard_repository=player_scorecard_repository,
            relationship_repository=relationship_repository,
        )

        self.knowledge_graph = KnowledgeGraphManager(
            knowledge_service=self.knowledge
        )

        self.propagation_planner = PropagationPlanner(
            knowledge_graph=self.knowledge_graph,
        )

        self.engine = CortexEngine(
            entity_resolver=EntityResolver(),
            player_enrichment=PlayerEnrichmentService(),
            signal_processor=SignalProcessor(),
            relationship_engine=RelationshipEngine(
                repository=relationship_repository,
                propagation_planner=self.propagation_planner,
            ),
            score_engine=ScoreEngine(
                repository=player_scorecard_repository,
            ),
            recommendation_engine=RecommendationEngine(),
            explanation_engine=ExplanationEngine(),
            player_snapshot_factory=PlayerSnapshotFactory(),
            player_intelligence_builder=PlayerIntelligenceBuilder(),
            trend_analyzer=TrendAnalyzer(),
            evidence_aggregator=evidence_aggregator,
            event_repository=event_repository,
            prediction_engine=PredictionEngine(),
        )


    def process_event(self, event: RawEvent):
        return self.engine.process_event(event)

    def get_player_scorecard(self, player_id: str):
        return self.knowledge.get_latest_scorecard(player_id)

    def get_player_history(self, player_id: str):
        return self.knowledge.get_scorecard_history(player_id)

    def get_relationships(self, entity_id: str):
        return {
            "outgoing": self.knowledge.get_outgoing_relationships(
                entity_id
            ),
            "incoming": self.knowledge.get_incoming_relationships(
                entity_id
            ),
        }

    def get_entity_graph(
        self,
        entity_id: str,
        max_depth: int = 2,
        direction: str = "outgoing",
    ):
        return self.knowledge_graph.build_graph(
            root_entity_id=entity_id,
            max_depth=max_depth,
            direction=direction,
        )

    def get_affected_entities(
        self,
        entity_id: str,
        max_depth: int = 2,
    ):
        return self.knowledge_graph.get_affected_entities(
            source_entity_id=entity_id,
            max_depth=max_depth,
        )

    def find_relationship_paths(
        self,
        source_entity_id: str,
        target_entity_id: str,
        max_depth: int = 3,
    ):
        return self.knowledge_graph.find_paths(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            max_depth=max_depth,
        )
