from datetime import datetime, timezone

import pytest

from gridiron_cortex.events import (
    CortexEvent,
    CortexEventBus,
    CortexEventType,
    InMemoryEventStore,
)


def event(
    event_type=CortexEventType.SIGNAL_CREATED,
    *,
    entity_id="player-1",
    correlation_id="corr-1",
):
    return CortexEvent(
        event_type=event_type,
        entity_id=entity_id,
        entity_name="Player One",
        source="test",
        payload={"score": 1.0},
        correlation_id=correlation_id,
        engine_version="cortex-test",
        timestamp=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
    )


def test_event_payload_is_immutable():
    created = event()
    with pytest.raises(TypeError):
        created.payload["score"] = 2.0


def test_event_round_trips_through_dict():
    created = event()
    restored = CortexEvent.from_dict(created.to_dict())
    assert restored == created
    assert restored.payload == {"score": 1.0}


def test_event_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        CortexEvent(
            event_type=CortexEventType.ARTICLE_RECEIVED,
            timestamp=datetime(2026, 8, 4, 12, 0),
        )


def test_publish_preserves_order_and_notifies_subscribers():
    bus = CortexEventBus()
    received = []
    bus.subscribe(received.append)

    first = event(CortexEventType.ARTICLE_RECEIVED)
    second = event(CortexEventType.SIGNAL_CREATED)
    bus.publish_many([first, second])

    assert received == [first, second]
    assert bus.history() == (first, second)


def test_typed_subscriber_receives_only_matching_events():
    bus = CortexEventBus()
    received = []
    bus.subscribe(received.append, CortexEventType.SCORE_UPDATED)

    bus.publish(event(CortexEventType.SIGNAL_CREATED))
    score_event = event(CortexEventType.SCORE_UPDATED)
    bus.publish(score_event)

    assert received == [score_event]


def test_unsubscribe_stops_delivery():
    bus = CortexEventBus()
    received = []
    unsubscribe = bus.subscribe(received.append)
    unsubscribe()
    bus.publish(event())
    assert received == []


def test_history_filters_by_type_entity_and_correlation():
    bus = CortexEventBus()
    expected = event(
        CortexEventType.RECOMMENDATION_CHANGED,
        entity_id="player-2",
        correlation_id="corr-2",
    )
    bus.publish(event())
    bus.publish(expected)

    assert bus.history(
        event_types=[CortexEventType.RECOMMENDATION_CHANGED],
        entity_id="player-2",
        correlation_id="corr-2",
    ) == (expected,)


def test_replay_returns_count_and_preserves_event_order():
    bus = CortexEventBus()
    first = event(CortexEventType.PLAYER_RESOLVED)
    second = event(CortexEventType.SIGNAL_CREATED)
    bus.publish_many([first, second])
    replayed = []

    count = bus.replay(replayed.append, correlation_id="corr-1")

    assert count == 2
    assert replayed == [first, second]


def test_latest_validates_limit_and_returns_tail():
    store = InMemoryEventStore()
    first = event(CortexEventType.ARTICLE_RECEIVED)
    second = event(CortexEventType.SIGNAL_CREATED)
    store.append(first)
    store.append(second)

    assert store.latest(1) == (second,)
    assert store.latest(0) == ()
    with pytest.raises(ValueError, match="limit"):
        store.latest(-1)
