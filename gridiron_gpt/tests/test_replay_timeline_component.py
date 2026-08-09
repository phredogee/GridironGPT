from datetime import datetime, timezone

import pytest

from apps.streamlit.components.replay_timeline import autoplay_next_position, build_replay_snapshot, replay_option_label, replay_position, stage_card_fields
from gridiron_cortex.events.event_types import CortexEventType
from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage, ReplayStep


def _step(stage, event_type, summary, details=None):
    return ReplayStep(event_id=f"evt-{stage.value}", timestamp=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc), stage=stage, event_type=event_type, title=stage.value.title(), summary=summary, entity_name="Tank Dell", details=details or {})

def _decision(*, recommendation="BUY", confidence=0.91):
    now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc); steps = (_step(ReplayStage.INGESTED, CortexEventType.ARTICLE_RECEIVED, "Article received"), _step(ReplayStage.UNDERSTOOD, CortexEventType.SIGNAL_CREATED, "Positive opportunity signal"), _step(ReplayStage.RECOMMENDED, CortexEventType.RECOMMENDATION_CHANGED, "Tank Dell moved to BUY.", {"recommendation": "BUY"}), _step(ReplayStage.CONFIDENCE, CortexEventType.CONFIDENCE_UPDATED, "Confidence increased", {"confidence": confidence}))
    return ReplayDecision(decision_id="abc123def456", correlation_id="corr-1", headline="Tank Dell returns to practice", started_at=now, completed_at=now, steps=steps, entity_name="Tank Dell", source="ESPN", recommendation=recommendation, confidence=confidence)

def test_replay_option_label_contains_player_action_and_decision_id(): assert replay_option_label(_decision()) == "Tank Dell · BUY · abc123def456"
def test_replay_option_label_handles_missing_recommendation(): assert replay_option_label(_decision(recommendation=None)) == "Tank Dell · abc123def456"
def test_snapshot_hides_future_steps_and_recommendation():
    snapshot = build_replay_snapshot(_decision(), 2); assert snapshot.step_number == 2; assert len(snapshot.visible_steps) == 2; assert snapshot.current.stage == ReplayStage.UNDERSTOOD; assert snapshot.recommendation is None; assert snapshot.confidence is None
def test_snapshot_reconstructs_recommendation_and_confidence():
    snapshot = build_replay_snapshot(_decision(), 4); assert snapshot.recommendation == "BUY"; assert snapshot.confidence == 0.91; assert snapshot.reached_stages == (ReplayStage.INGESTED, ReplayStage.UNDERSTOOD, ReplayStage.RECOMMENDED, ReplayStage.CONFIDENCE)
def test_snapshot_bounds_requested_position():
    decision = _decision(); assert build_replay_snapshot(decision, 0).step_number == 1; assert build_replay_snapshot(decision, 999).step_number == len(decision.steps)
def test_replay_navigation_moves_one_step_and_to_boundaries():
    assert replay_position(3, 5, "previous") == 2; assert replay_position(3, 5, "next") == 4; assert replay_position(3, 5, "beginning") == 1; assert replay_position(3, 5, "end") == 5
def test_replay_navigation_does_not_move_past_boundaries(): assert replay_position(1, 5, "previous") == 1; assert replay_position(5, 5, "next") == 5
def test_replay_navigation_rejects_unknown_action():
    with pytest.raises(ValueError, match="Unknown replay action"): replay_position(2, 5, "teleport")
def test_stage_card_fields_extract_signal_intelligence():
    step = _step(ReplayStage.UNDERSTOOD, CortexEventType.SIGNAL_CREATED, "signal", {"signal_category": "opportunity", "impact_score": 0.75, "confidence": 0.88}); assert stage_card_fields(step) == (("Type", "Opportunity"), ("Impact", "+0.750"), ("Signal Confidence", "88%"))
def test_stage_card_fields_extract_propagation_intelligence():
    step = _step(ReplayStage.PROPAGATED, CortexEventType.PROPAGATION_COMPLETED, "propagated", {"impact_count": 2, "impacts": [{"entity_name": "Nico Collins", "relationship_type": "teammate", "propagation_weight": 0.35, "projected_impact": 0.21}]}); assert stage_card_fields(step) == (("Impacts", "2"), ("Target", "Nico Collins"), ("Relationship", "Teammate"), ("Weight", "+0.350"), ("Projected Impact", "+0.210"))
def test_stage_card_fields_extract_score_and_recommendation():
    score = _step(ReplayStage.SCORED, CortexEventType.SCORE_UPDATED, "score", {"previous_score": 50.0, "new_score": 51.2, "score_delta": 1.2}); rec = _step(ReplayStage.RECOMMENDED, CortexEventType.RECOMMENDATION_CHANGED, "rec", {"previous_recommendation": "HOLD", "recommendation": "BUY", "confidence": 0.91}); assert ("Delta", "+1.200") in stage_card_fields(score); assert stage_card_fields(rec) == (("Previous", "HOLD"), ("Recommendation", "BUY"), ("Confidence", "91%"))
def test_autoplay_advances_and_keeps_playing_before_final_step(): assert autoplay_next_position(2, 5) == (3, True)
def test_autoplay_stops_when_it_reaches_final_step(): assert autoplay_next_position(4, 5) == (5, False); assert autoplay_next_position(5, 5) == (5, False)
