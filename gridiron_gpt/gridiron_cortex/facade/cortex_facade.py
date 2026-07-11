from pathlib import Path

from gridiron_cortex.engine.cortex_engine import CortexEngine
from gridiron_cortex.engine.entity_resolver import EntityResolver
from gridiron_cortex.engine.explanation_engine import ExplanationEngine
from gridiron_cortex.engine.recommendation_engine import RecommendationEngine
from gridiron_cortex.engine.relationship_engine import RelationshipEngine
from gridiron_cortex.engine.score_engine import ScoreEngine
from gridiron_cortex.engine.signal_processor import SignalProcessor
from gridiron_cortex.knowledge.knowledge_service import KnowledgeService
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.storage.json_event_repository import JsonEventRepository
from gridiron_cortex.storage.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_cortex.storage.json_relationship_repository import (
    JsonRelationshipRepository,
)
from gridiron_cortex.knowledge.knowledge_graph_manager import (
    KnowledgeGraphManager,
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

        self.engine = CortexEngine(
            entity_resolver=EntityResolver(),
            signal_processor=SignalProcessor(),
            relationship_engine=RelationshipEngine(
                repository=relationship_repository,
            ),
            score_engine=ScoreEngine(
                repository=player_scorecard_repository,
            ),
            recommendation_engine=RecommendationEngine(),
            explanation_engine=ExplanationEngine(),
            event_repository=event_repository,
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
