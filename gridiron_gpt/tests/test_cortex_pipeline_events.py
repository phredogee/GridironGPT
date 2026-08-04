from dataclasses import dataclass
from types import SimpleNamespace

from gridiron_cortex.events import (
    CortexEventBus,
    CortexEventType,
    PipelineEventPublisher,
)
from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.models.raw_event import RawEvent


@dataclass
class ScoreUpdate:
    entity_id: str
    entity_name: str
    score_delta: float


@dataclass
class Recommendation:
    entity_id: str
    entity_name: str
    action: str
    confidence: float


def result_fixture():
    entity = SimpleNamespace(
        player_id="tank-dell",
        name="Tank Dell",
        entity_type="player",
        team="HOU",
        position="WR",
        confidence=0.98,
    )
    signal = SimpleNamespace(
        headline="Tank Dell returns to first-team practice",
        entities=[entity],
        impact_score=1.0,
        sentiment="positive",
        signal_type="news",
        signal_category="opportunity",
        confidence=0.91,
    )
    return SimpleNamespace(
        event=SimpleNamespace(source="ESPN"),
        entities=[entity],
        signal=signal,
        impacts=[{"entity_name": "HOU", "impact_score": 0.3}],
        score_updates=[ScoreUpdate("tank-dell", "Tank Dell", 1.0)],
        recommendations=[
            Recommendation("tank-dell", "Tank Dell", "BUY", 0.91)
        ],
        confidence_result=None,
    )


def test_pipeline_publisher_emits_ordered_correlated_trail():
    bus = CortexEventBus()
    publisher = PipelineEventPublisher(bus, engine_version="cortex-test")
    raw = RawEvent(
        headline="Tank Dell returns to first-team practice",
        source="ESPN",
        player="Tank Dell",
        player_id="tank-dell",
        team="HOU",
    )
    correlation_id = raw.fingerprint()

    publisher.article_received(raw, correlation_id)
    publisher.publish_result(result_fixture(), correlation_id)

    events = bus.history(correlation_id=correlation_id)
    assert [event.event_type for event in events] == [
        CortexEventType.ARTICLE_RECEIVED,
        CortexEventType.PLAYER_RESOLVED,
        CortexEventType.SIGNAL_CREATED,
        CortexEventType.PROPAGATION_COMPLETED,
        CortexEventType.SCORE_UPDATED,
        CortexEventType.RECOMMENDATION_CHANGED,
        CortexEventType.CONFIDENCE_UPDATED,
    ]
    assert {event.correlation_id for event in events} == {correlation_id}
    assert {event.engine_version for event in events} == {"cortex-test"}


def test_pipeline_events_include_activity_feed_payloads():
    bus = CortexEventBus()
    publisher = PipelineEventPublisher(bus)
    publisher.publish_result(result_fixture(), "run-1")

    signal = bus.history(
        event_types=[CortexEventType.SIGNAL_CREATED]
    )[0]
    propagation = bus.history(
        event_types=[CortexEventType.PROPAGATION_COMPLETED]
    )[0]
    recommendation = bus.history(
        event_types=[CortexEventType.RECOMMENDATION_CHANGED]
    )[0]

    assert signal.payload["impact_score"] == 1.0
    assert signal.payload["signal_category"] == "opportunity"
    assert propagation.payload["impact_count"] == 1
    assert recommendation.payload["action"] == "BUY"


def test_pipeline_publisher_omits_empty_optional_stages():
    bus = CortexEventBus()
    publisher = PipelineEventPublisher(bus)
    result = SimpleNamespace(
        event=SimpleNamespace(source="ESPN"),
        entities=[],
        signal=None,
        impacts=[],
        score_updates=[],
        recommendations=[],
        confidence_result=None,
    )

    assert publisher.publish_result(result, "run-empty") == ()
    assert bus.history(correlation_id="run-empty") == ()


def test_facade_process_event_publishes_before_and_after_engine():
    raw = RawEvent(
        headline="Tank Dell returns",
        source="ESPN",
        player="Tank Dell",
        player_id="tank-dell",
    )
    facade = CortexFacade.__new__(CortexFacade)
    facade.event_bus = CortexEventBus()
    facade.pipeline_events = PipelineEventPublisher(facade.event_bus)
    facade.engine = SimpleNamespace(process_event=lambda event: result_fixture())

    returned = facade.process_event(raw)
    events = facade.get_event_history(correlation_id=raw.fingerprint())

    assert returned is not None
    assert events[0].event_type is CortexEventType.ARTICLE_RECEIVED
    assert events[-1].event_type is CortexEventType.CONFIDENCE_UPDATED


def test_facade_exposes_latest_pipeline_events():
    facade = CortexFacade.__new__(CortexFacade)
    facade.event_bus = CortexEventBus()
    publisher = PipelineEventPublisher(facade.event_bus)
    raw = RawEvent(headline="One", source="ESPN")
    publisher.article_received(raw, "one")
    publisher.article_received(raw, "two")

    latest = facade.get_latest_events(limit=1)
    assert len(latest) == 1
    assert latest[0].correlation_id == "two"
