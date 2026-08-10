from datetime import datetime, timedelta, timezone

from gridiron_cortex.activity import (
    ActivityFeedService,
    ActivitySeverity,
    format_activity,
    group_activity,
)
from gridiron_cortex.events import CortexEvent, CortexEventBus, CortexEventType


NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def event(event_type, *, correlation="run-1", seconds=0, **kwargs):
    return CortexEvent(
        event_type=event_type,
        correlation_id=correlation,
        timestamp=NOW + timedelta(seconds=seconds),
        **kwargs,
    )


def test_formatter_builds_readable_article_card():
    card = format_activity(
        event(
            CortexEventType.ARTICLE_RECEIVED,
            source="ESPN",
            payload={"headline": "Tank Dell returns to practice"},
        )
    )

    assert card.icon == "📰"
    assert card.title == "Article received"
    assert card.subtitle == "Tank Dell returns to practice"
    assert card.source == "ESPN"


def test_formatter_marks_positive_and_negative_signals():
    positive = format_activity(
        event(
            CortexEventType.SIGNAL_CREATED,
            payload={"impact_score": 0.75, "signal_category": "opportunity"},
        )
    )
    negative = format_activity(
        event(
            CortexEventType.SIGNAL_CREATED,
            payload={"impact_score": -0.5, "signal_category": "health"},
        )
    )

    assert positive.severity == ActivitySeverity.POSITIVE
    assert negative.severity == ActivitySeverity.NEGATIVE
    assert "Opportunity" in positive.subtitle
    assert "+0.75" in positive.subtitle


def test_group_activity_combines_one_correlation_story():
    cards = [
        format_activity(
            event(
                CortexEventType.ARTICLE_RECEIVED,
                payload={"headline": "Player practices"},
            )
        ),
        format_activity(
            event(
                CortexEventType.SIGNAL_CREATED,
                seconds=1,
                entity_name="Player",
                payload={"impact_score": 1.0},
            )
        ),
    ]

    groups = group_activity(cards)

    assert len(groups) == 1
    assert groups[0].headline == "Player practices"
    assert groups[0].event_count == 2
    assert [card.event_type for card in groups[0].cards] == [
        CortexEventType.ARTICLE_RECEIVED,
        CortexEventType.SIGNAL_CREATED,
    ]


def test_group_activity_sorts_newest_story_first():
    groups = group_activity(
        [
            format_activity(
                event(
                    CortexEventType.ARTICLE_RECEIVED,
                    correlation="old",
                    payload={"headline": "Old"},
                )
            ),
            format_activity(
                event(
                    CortexEventType.ARTICLE_RECEIVED,
                    correlation="new",
                    seconds=10,
                    payload={"headline": "New"},
                )
            ),
        ]
    )

    assert [group.correlation_id for group in groups] == ["new", "old"]


def test_feed_service_filters_by_event_type():
    bus = CortexEventBus()
    bus.publish(event(CortexEventType.ARTICLE_RECEIVED))
    bus.publish(event(CortexEventType.SIGNAL_CREATED, seconds=1))
    service = ActivityFeedService(bus)

    groups = service.by_type(CortexEventType.SIGNAL_CREATED)

    assert len(groups) == 1
    assert [card.event_type for card in groups[0].cards] == [
        CortexEventType.SIGNAL_CREATED
    ]


def test_feed_service_filters_by_player_name():
    bus = CortexEventBus()
    bus.publish(
        event(
            CortexEventType.PLAYER_RESOLVED,
            correlation="tank",
            entity_name="Tank Dell",
        )
    )
    bus.publish(
        event(
            CortexEventType.PLAYER_RESOLVED,
            correlation="gibbs",
            entity_name="Jahmyr Gibbs",
        )
    )
    service = ActivityFeedService(bus)

    groups = service.by_player("tank dell")

    assert len(groups) == 1
    assert groups[0].entity_name == "Tank Dell"


def test_feed_service_returns_correlation_story_and_empty_limits():
    bus = CortexEventBus()
    bus.publish(
        event(
            CortexEventType.ARTICLE_RECEIVED,
            correlation="story",
            payload={"headline": "Story headline"},
        )
    )
    bus.publish(
        event(
            CortexEventType.CONFIDENCE_UPDATED,
            correlation="story",
            seconds=1,
            payload={"confidence": 0.91},
        )
    )
    service = ActivityFeedService(bus)

    story = service.by_correlation("story")

    assert story is not None
    assert story.headline == "Story headline"
    assert story.event_count == 2
    assert service.latest(limit=0) == ()
