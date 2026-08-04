from datetime import datetime, timezone

from apps.streamlit.components.replay_timeline import replay_option_label
from gridiron_cortex.events.event_types import CortexEventType
from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage, ReplayStep


def _decision(*, recommendation="BUY", confidence=0.91):
    now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
    step = ReplayStep(
        event_id="evt-1",
        timestamp=now,
        stage=ReplayStage.RECOMMENDED,
        event_type=CortexEventType.RECOMMENDATION_CHANGED,
        title="Recommendation changed",
        summary="Tank Dell moved to BUY.",
        entity_name="Tank Dell",
    )
    return ReplayDecision(
        decision_id="abc123def456",
        correlation_id="corr-1",
        headline="Tank Dell returns to practice",
        started_at=now,
        completed_at=now,
        steps=(step,),
        entity_name="Tank Dell",
        source="ESPN",
        recommendation=recommendation,
        confidence=confidence,
    )


def test_replay_option_label_contains_player_action_and_decision_id():
    assert replay_option_label(_decision()) == "Tank Dell · BUY · abc123def456"


def test_replay_option_label_handles_missing_recommendation():
    assert replay_option_label(_decision(recommendation=None)) == "Tank Dell · abc123def456"
