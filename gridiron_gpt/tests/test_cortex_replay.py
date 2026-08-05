from datetime import datetime, timedelta, timezone

import pytest

from gridiron_cortex.events import CortexEvent, CortexEventBus, CortexEventType
from gridiron_cortex.replay import ReplayEngine, ReplayStage, build_replay_decision


BASE = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def event(event_type, minute, *, correlation="run-1", entity="Tank Dell", payload=None):
    return CortexEvent(event_type=event_type, timestamp=BASE + timedelta(minutes=minute), correlation_id=correlation, entity_id="tank-dell", entity_name=entity, source="ESPN", payload=payload or {}, event_id=f"{correlation}-{minute}-{event_type.value}")


def complete_events(correlation="run-1"):
    return (
        event(CortexEventType.ARTICLE_RECEIVED, 0, correlation=correlation, payload={"headline": "Tank Dell returns to practice"}),
        event(CortexEventType.PLAYER_RESOLVED, 1, correlation=correlation, payload={"entity_type": "player", "team": "HOU", "position": "WR", "confidence": 0.98}),
        event(CortexEventType.SIGNAL_CREATED, 2, correlation=correlation, payload={"signal_category": "opportunity", "impact_score": 0.74}),
        event(CortexEventType.PROPAGATION_COMPLETED, 3, correlation=correlation, payload={"impact_count": 2}),
        event(CortexEventType.SCORE_UPDATED, 4, correlation=correlation, payload={"score_delta": 0.72}),
        event(CortexEventType.RECOMMENDATION_CHANGED, 5, correlation=correlation, payload={"recommendation": "BUY", "confidence": 0.91}),
        event(CortexEventType.CONFIDENCE_UPDATED, 6, correlation=correlation, payload={"confidence": 0.91}),
    )


def test_replay_builder_orders_pipeline_stages():
    decision = build_replay_decision(reversed(complete_events()))
    assert decision is not None
    assert [step.stage for step in decision.steps] == [ReplayStage.INGESTED, ReplayStage.RESOLVED, ReplayStage.UNDERSTOOD, ReplayStage.PROPAGATED, ReplayStage.SCORED, ReplayStage.RECOMMENDED, ReplayStage.CONFIDENCE]


def test_replay_exposes_decision_summary():
    decision = build_replay_decision(complete_events())
    assert decision is not None
    assert decision.headline == "Tank Dell returns to practice"
    assert decision.entity_name == "Tank Dell"
    assert decision.recommendation == "BUY"
    assert decision.confidence == 0.91
    assert decision.is_complete is True
    assert len(decision.decision_id) == 12


def test_replay_decision_id_is_stable():
    first = build_replay_decision(complete_events()); second = build_replay_decision(complete_events())
    assert first is not None and second is not None
    assert first.decision_id == second.decision_id


def test_replay_rejects_mixed_correlations():
    mixed = complete_events("run-a")[:2] + complete_events("run-b")[:2]
    with pytest.raises(ValueError, match="correlation_id"):
        build_replay_decision(mixed)


def test_replay_engine_returns_latest_and_by_player():
    bus = CortexEventBus(); bus.publish_many(complete_events("older"))
    newer = tuple(CortexEvent(event_type=item.event_type, timestamp=item.timestamp + timedelta(hours=1), correlation_id="newer", entity_id=item.entity_id, entity_name="Jahmyr Gibbs", source=item.source, payload=dict(item.payload), event_id=f"newer-{item.event_id}") for item in complete_events("template"))
    bus.publish_many(newer); replay = ReplayEngine(bus)
    assert replay.latest(limit=1)[0].correlation_id == "newer"
    assert replay.by_player("jahmyr gibbs")[0].correlation_id == "newer"


def test_replay_engine_finds_decision_and_handles_empty_history():
    empty = ReplayEngine(CortexEventBus())
    assert empty.latest() == ()
    assert empty.by_correlation("missing") is None
    bus = CortexEventBus(); bus.publish_many(complete_events()); replay = ReplayEngine(bus); decision = replay.by_correlation("run-1")
    assert decision is not None
    assert replay.by_decision_id(decision.decision_id) == decision


def test_resolved_steps_use_entity_specific_titles():
    events = list(complete_events())
    events.insert(2, event(CortexEventType.PLAYER_RESOLVED, 1, entity="HOU", payload={"entity_type": "team", "confidence": 0.9}))
    decision = build_replay_decision(events)
    assert decision is not None
    resolved_titles = [step.title for step in decision.steps if step.stage == ReplayStage.RESOLVED]
    assert resolved_titles == ["Player resolved", "Team resolved"]


def test_replay_recovers_nonzero_recommendation_confidence_when_direct_value_is_zero():
    events = list(complete_events())
    events[-1] = event(CortexEventType.CONFIDENCE_UPDATED, 6, payload={"confidence": 0.0, "recommendation_confidences": [0.87], "signal_confidence": 0.75})
    decision = build_replay_decision(events)
    assert decision is not None
    assert decision.confidence == 0.87
    assert decision.steps[-1].summary == "Confidence 87%"
