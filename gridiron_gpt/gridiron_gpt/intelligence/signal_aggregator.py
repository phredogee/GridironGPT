"""Aggregate nflverse signals into interpretable player trends."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def _player_key(signal: dict[str, Any]) -> str:
    """Return the most stable available player identifier."""
    return str(
        signal.get("player_id")
        or signal.get("player_name")
        or ""
    ).strip()


def _signal_week(signal: dict[str, Any]) -> int:
    """Return the signal's effective week."""
    week = (
        signal.get("current_week")
        or signal.get("week")
        or 0
    )

    try:
        return int(week)
    except (TypeError, ValueError):
        return 0


def _signal_method(signal: dict[str, Any]) -> str:
    """Return a normalized signal-generation method."""
    method = signal.get("signal_method")

    if method:
        return str(method)

    if "previous_week" in signal:
        return "weekly_delta"

    return "unknown"


def _group_key(signal: dict[str, Any]) -> tuple[str, str, int]:
    """Group by player, metric, and season."""
    player = _player_key(signal)
    metric = str(signal.get("metric") or "unknown")

    try:
        season = int(signal.get("season") or 0)
    except (TypeError, ValueError):
        season = 0

    return player, metric, season


def _latest_signal(
    signals: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return the latest signal by week."""
    return max(
        signals,
        key=_signal_week,
    )


def _classify_trend(
    signals: list[dict[str, Any]],
) -> str:
    """
    Classify a group of signals.

    emerging:
        One recent signal without supporting evidence.

    confirmed:
        Weekly and rolling methods agree in the latest week.

    sustained:
        The same direction appears in at least three distinct weeks.

    volatile:
        Both positive and negative directions appear in the recent window.
    """
    if not signals:
        return "emerging"

    ordered = sorted(
        signals,
        key=_signal_week,
    )

    recent = ordered[-4:]
    recent_directions = {
        _direction_polarity(signal)
        for signal in recent
        if _direction_polarity(signal) != "unknown"
    }

    if len(recent_directions) > 1:
        return "volatile"

    latest_week = _signal_week(ordered[-1])

    latest_week_signals = [
        signal
        for signal in ordered
        if _signal_week(signal) == latest_week
    ]

    latest_methods = {
        _signal_method(signal)
        for signal in latest_week_signals
    }

    latest_directions = {
        _direction_polarity(signal)
        for signal in latest_week_signals
        if _direction_polarity(signal) != "unknown"
    }

    if (
        "weekly_delta" in latest_methods
        and "rolling_baseline" in latest_methods
        and len(latest_directions) == 1
    ):
        return "confirmed"

    recent_week_polarities: dict[int, set[str]] = defaultdict(set)

    for signal in ordered:
        week = _signal_week(signal)
        polarity = _direction_polarity(signal)

        if week <= 0 or polarity == "unknown":
            continue

        recent_week_polarities[week].add(polarity)

    recent_weeks = sorted(recent_week_polarities)[-3:]

    if len(recent_weeks) == 3:
        recent_polarities = {
            next(iter(recent_week_polarities[week]))
            for week in recent_weeks
            if len(recent_week_polarities[week]) == 1
        }

        if len(recent_polarities) == 1:
            return "sustained"

    return "emerging"


def _aggregate_confidence(
    signals: list[dict[str, Any]],
    classification: str,
) -> float:
    """Combine source confidence with a trend-strength bonus."""
    confidences = [
        float(signal.get("confidence") or 0.0)
        for signal in signals
    ]

    base_confidence = (
        mean(confidences)
        if confidences
        else 0.0
    )

    bonus_by_classification = {
        "emerging": 0.00,
        "confirmed": 0.05,
        "sustained": 0.07,
        "volatile": -0.12,
    }

    combined = (
        base_confidence
        + bonus_by_classification[classification]
    )

    return round(
        max(0.0, min(1.0, combined)),
        3,
    )


def _aggregate_impact(
    signals: list[dict[str, Any]],
    classification: str,
) -> float:
    """Combine impact values without double-counting evidence."""
    impacts = [
        float(signal.get("impact_score") or 0.0)
        for signal in signals
    ]

    if not impacts:
        return 0.0

    average_impact = mean(impacts)

    multiplier_by_classification = {
        "emerging": 0.75,
        "confirmed": 1.00,
        "sustained": 1.10,
        "volatile": 0.40,
    }

    combined = (
        average_impact
        * multiplier_by_classification[classification]
    )

    return round(
        max(-1.0, min(1.0, combined)),
        3,
    )


def aggregate_signals(
    weekly_signals: list[dict[str, Any]],
    rolling_signals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Combine weekly and rolling signals into trend summaries.

    Returns one aggregate per player, metric, and season.
    """
    combined_signals = [
        {
            **signal,
            "signal_method": _signal_method(signal),
        }
        for signal in weekly_signals + rolling_signals
    ]

    grouped: dict[
        tuple[str, str, int],
        list[dict[str, Any]],
    ] = defaultdict(list)

    for signal in combined_signals:
        player = _player_key(signal)

        if not player:
            continue

        grouped[_group_key(signal)].append(signal)

    aggregates: list[dict[str, Any]] = []

    for (
        player_key,
        metric,
        season,
    ), signals in grouped.items():
        ordered = sorted(
            signals,
            key=_signal_week,
        )

        latest = _latest_signal(ordered)
        classification = _classify_trend(ordered)

        weeks = sorted(
            {
                _signal_week(signal)
                for signal in ordered
                if _signal_week(signal) > 0
            }
        )

        methods = sorted(
            {
                _signal_method(signal)
                for signal in ordered
            }
        )

        directions = [
            _direction_polarity(signal)
            for signal in ordered
            if _direction_polarity(signal) != "unknown"
        ]

        latest_direction = str(
            latest.get("direction") or ""
        )

        supporting_reasons = [
            str(signal.get("reason"))
            for signal in ordered[-5:]
            if signal.get("reason")
        ]

        aggregates.append(
            {
                "source": "nflverse",
                "player_id": latest.get("player_id")
                or player_key,
                "player_name": latest.get("player_name")
                or player_key,
                "team": latest.get("team") or "",
                "position": latest.get("position") or "",
                "season": season,
                "metric": metric,
                "signal_type": latest.get("signal_type")
                or "unknown",
                "trend_classification": classification,
                "direction": latest_direction,
                "sentiment": latest.get("sentiment")
                or "",
                "latest_week": _signal_week(latest),
                "weeks": weeks,
                "methods": methods,
                "evidence_count": len(ordered),
                "direction_count": {
                    "positive": directions.count("positive"),
                    "negative": directions.count("nagative"),
                },
                "confidence": _aggregate_confidence(
                    ordered,
                    classification,
                ),
                "impact_score": _aggregate_impact(
                    ordered,
                    classification,
                ),
                "reasons": supporting_reasons,
            }
        )

    return sorted(
        aggregates,
        key=lambda item: (
            abs(item["impact_score"]),
            item["confidence"],
        ),
        reverse=True,
    )

def _direction_polarity(signal: dict[str, Any]) -> str:
    """Normalize direction wording into positive or negative polarity."""
    direction = str(signal.get("direction") or "").casefold()

    if direction in {"increased", "above", "positive", "up"}:
        return "positive"

    if direction in {"decreased", "below", "negative", "down"}:
        return "negative"

    sentiment = str(signal.get("sentiment") or "").casefold()

    if sentiment in {"positive", "negative"}:
        return sentiment

    return "unknown"
