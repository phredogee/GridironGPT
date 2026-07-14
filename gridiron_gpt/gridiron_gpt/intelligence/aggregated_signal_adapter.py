"""
Convert aggregated statistical trends into Cortex RawEvents.
"""

from __future__ import annotations

from typing import Any

from gridiron_cortex.models.raw_event import RawEvent


TREND_EVENT_TYPES = {
    "opportunity": "opportunity_trend",
    "production": "production_trend",
}


def aggregate_to_raw_event(
    aggregate: dict[str, Any],
) -> RawEvent:
    """Convert one aggregated statistical trend into a Cortex RawEvent."""
    signal_type = str(
        aggregate.get("signal_type") or "unknown"
    )

    event_type = TREND_EVENT_TYPES.get(
        signal_type,
        "statistical_trend",
    )

    player_name = str(
        aggregate.get("player_name") or "Unknown"
    )

    metric = str(
        aggregate.get("metric") or "metric"
    ).replace("_", " ")

    classification = str(
        aggregate.get("trend_classification") or "emerging"
    )

    sentiment = str(
        aggregate.get("sentiment") or "neutral"
    )

    latest_week = aggregate.get("latest_week")

    if sentiment == "positive":
        direction_text = "increased"
    elif sentiment == "negative":
        direction_text = "decreased"
    else:
        direction_text = "changed"

    headline = (
        f"{player_name} {metric} {direction_text}; "
        f"{classification} {signal_type} trend"
    )

    return RawEvent(
        headline=headline,
        source=aggregate.get("source", "nflverse"),
        player=player_name,
        team=aggregate.get("team"),
        event_type=event_type,
        published_at=(
            f"{aggregate.get('season')}-W{latest_week}"
            if aggregate.get("season") and latest_week
            else None
        ),
        url=None,
    )


def aggregates_to_events(
    aggregates: list[dict[str, Any]],
) -> list[RawEvent]:
    """Convert every aggregate into a RawEvent."""
    return [
        aggregate_to_raw_event(item)
        for item in aggregates
    ]
