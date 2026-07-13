from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.engine.cortex_engine import CortexEngine
from gridiron_cortex.engine.entity_resolver import EntityResolver
from gridiron_cortex.engine.signal_processor import SignalProcessor
from gridiron_cortex.engine.relationship_engine import RelationshipEngine
from gridiron_cortex.engine.score_engine import ScoreEngine
from gridiron_cortex.engine.recommendation_engine import RecommendationEngine
from gridiron_cortex.engine.explanation_engine import ExplanationEngine
from gridiron_cortex.storage.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_cortex.storage.json_event_repository import (
    JsonEventRepository,
)
from gridiron_cortex.storage.json_relationship_repository import (
    JsonRelationshipRepository,
)


event_repository = JsonEventRepository(
    "data/cortex/events.jsonl"
)

scorecard_repository = JsonPlayerScorecardRepository(
    "data/cortex/player_scorecards.jsonl"
)

relationship_repository = JsonRelationshipRepository(
    "data/cortex/relationships.jsonl"
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
)

sample_event = RawEvent(
    headline="CJ Stroud returns to practice and looks sharp with the first-team offense.",
    source="relationship_test",
    player="CJ Stroud",
    team="HOU",
)

result = engine.process_event(sample_event)

print(result)
