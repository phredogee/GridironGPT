from datetime import datetime, timedelta, timezone

import pytest

from apps.streamlit.components.activity_feed import (
    relative_time,
    summarize_activity_group,
)
from gridiron_cortex.activity.activity_models import (
    ActivityCard,
    ActivityGroup,
    ActivitySeverity,
)
from gridiron_cortex.events.event_types import CortexEventType


def card(timestamp: datetime) -> ActivityCard:
    return ActivityCard(
        event_id="event-1",
        timestamp=timestamp,
        event_type=CortexEventType.ARTICLE_RECEIVED,
        icon="NEWS",
        title="Article received",
        subtitle="Tank Dell returns to practice",
        severity=ActivitySeverity.INFO,
        correlation_id="run-1",
        entity_name="Tank Dell",
        source="ESPN",
    )


def test_relative_time_formats_recent_activity():
    now = datetime(2026, 8, 4, 17, 30, tzinfo=timezone.utc)

    assert relative_time(now - timedelta(seconds=20), now=now) == "just now"
    assert relative_time(now - timedelta(minutes=7), now=now) == "7m ago"
    assert relative_time(now - timedelta(hours=3), now=now) == "3h ago"
    assert relative_time(now - timedelta(days=2), now=now) == "2d ago"


def test_relative_time_requires_timezone_aware_values():
    naive = datetime(2026, 8, 4, 12, 30)

    with pytest.raises(ValueError, match="timestamp must be timezone-aware"):
        relative_time(naive)


def test_activity_group_summary_includes_story_context():
    timestamp = datetime(2026, 8, 4, 17, 30, tzinfo=timezone.utc)
    group = ActivityGroup(
        correlation_id="run-1",
        headline="Tank Dell returns to practice",
        timestamp=timestamp,
        cards=(card(timestamp),),
        source="ESPN",
        entity_name="Tank Dell",
    )

    assert summarize_activity_group(group) == (
        "Tank Dell returns to practice · Tank Dell · ESPN · 1 events"
    )
