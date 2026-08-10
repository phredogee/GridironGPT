"""Generate meaningful player signals from nflverse weekly-stat changes."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


METRIC_RULES: dict[str, dict[str, Any]] = {
    "targets": {
        "signal_type": "opportunity",
        "minimum_delta": 3.0,
        "weight": 0.18,
        "label": "Targets",
    },
    "receptions": {
        "signal_type": "production",
        "minimum_delta": 3.0,
        "weight": 0.12,
        "label": "Receptions",
    },
    "carries": {
        "signal_type": "opportunity",
        "minimum_delta": 4.0,
        "weight": 0.12,
        "label": "Carries",
    },
    "rushing_yards": {
        "signal_type": "production",
        "minimum_delta": 40.0,
        "weight": 0.08,
        "label": "Rushing yards",
    },
    "receiving_yards": {
        "signal_type": "production",
        "minimum_delta": 40.0,
        "weight": 0.008,
        "label": "Receiving yards",
    },
    "passing_yards": {
        "signal_type": "production",
        "minimum_delta": 100.0,
        "weight": 0.003,
        "label": "Passing yards",
    },
    "rushing_tds": {
        "signal_type": "production",
        "minimum_delta": 1.0,
        "weight": 0.20,
        "label": "Rushing touchdowns",
    },
    "receiving_tds": {
        "signal_type": "production",
        "minimum_delta": 1.0,
        "weight": 0.20,
        "label": "Receiving touchdowns",
    },
    "passing_tds": {
        "signal_type": "production",
        "minimum_delta": 2.0,
        "weight": 0.12,
        "label": "Passing touchdowns",
    },
}


def _number(value: Any) -> float:
    """Safely convert a statistical value to float."""
    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def _player_key(record: dict[str, Any]) -> str:
    """Return the most stable available player identifier."""
    return str(
        record.get("player_id")
        or record.get("gsis_id")
        or record.get("player_name")
        or record.get("player_display_name")
        or ""
    ).strip()

def _player_name(record: dict[str, Any]) -> str:
    return str(
        record.get("player_name")
        or record.get("player_display_name")
        or record.get("display_name")
        or "Unknown"
    ).strip()

def _statistics(record: dict[str, Any]) -> dict[str, Any]:
    """Support normalized and raw nflverse rows."""
    statistics = record.get("statistics")

    if isinstance(statistics, dict):
        return statistics

    return record

def compare_weekly_records(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Compare two weekly records for one player.

    Only changes exceeding configured thresholds become signals.
    """
    previous_stats = _statistics(previous)
    current_stats = _statistics(current)

    player_id = _player_key(current) or _player_key(previous)
    player_name = _player_name(current)
    team = str(
        current.get("team")
        or current.get("recent_team")
        or previous.get("team")
        or previous.get("recent_team")
        or ""
    )
    position = str(
        current.get("position")
        or current.get("position_group")
        or previous.get("position")
        or previous.get("position_group")
        or ""
    )

    previous_week = previous.get("week")
    current_week = current.get("week")
    season = current.get("season") or previous.get("season")

    week_gap = (
        current_week - previous_week
        if isinstance(previous_week, int)
        and isinstance(current_week, int)
        else None
    )

    signals: list[dict[str, Any]] = []

    for metric, rule in METRIC_RULES.items():
        old_value = _number(previous_stats.get(metric))
        new_value = _number(current_stats.get(metric))
        delta = new_value - old_value

        # Position-specific thresholds
        if metric == "carries" and position.upper() == "QB":
            minimum_delta = 6.0
            weight = 0.06
        else:
            minimum_delta = rule["minimum_delta"]
            weight = rule["weight"]

        if abs(delta) < minimum_delta:
            continue

        direction = "increased" if delta > 0 else "decreased"
        sentiment = "positive" if delta > 0 else "negative"

        impact_score = round(
            max(-1.0, min(1.0, delta * weight)),
            3,
        )

        percent_change = None

        if old_value != 0:
            percent_change = round((delta / abs(old_value)) * 100, 1)

        period_label = (
            f"between Weeks {previous_week} and {current_week}"
            if week_gap == 1
            else f"across Weeks {previous_week} to {current_week}"
        )

        reason = (
            f"{rule['label']} {direction} from "
            f"{old_value:g} to {new_value:g} "
            f"({delta:+g}) {period_label}."
        )

        confidence = (
            0.92
            if rule["signal_type"] == "opportunity"
            else 0.72
        )

        signals.append(
            {
                "source": "nflverse",
                "signal_type": rule["signal_type"],
                "metric": metric,
                "player_id": player_id,
                "player_name": player_name,
                "team": team,
                "position": position,
                "season": season,
                "week_gap": week_gap,
                "previous_week": previous_week,
                "current_week": current_week,
                "previous_value": old_value,
                "current_value": new_value,
                "delta": delta,
                "percent_change": percent_change,
                "direction": direction,
                "sentiment": sentiment,
                "impact_score": impact_score,
                "confidence": confidence,
                "reason": reason,
            }
        )

    return signals


def generate_weekly_signals(
    records: list[dict[str, Any]],
    include_postseason: bool = False,
) -> list[dict[str, Any]]:
    """
    Generate signals by comparing adjacent weeks for every player.

    Records may be raw nflverse rows or normalized weekly-stat rows.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        player_key = _player_key(record)

        if not player_key:
            continue

        grouped[player_key].append(record)

    generated: list[dict[str, Any]] = []

    for player_records in grouped.values():
        ordered = sorted(
            player_records,
            key=lambda item: (
                item.get("season") or 0,
                item.get("week") or 0,
            ),
        )

        for previous, current in zip(ordered, ordered[1:]):
            previous_season = previous.get("season")
            current_season = current.get("season")

            if previous_season != current_season:
                continue

            previous_week = previous.get("week")
            current_week = current.get("week")

            if previous_week is None or current_week is None:
                continue

            if (
                not include_postseason
                and isinstance(current_week, int)
                and current_week > 18
            ):
                continue

            week_gap = current_week - previous_week
            if week_gap <= 0:
                continue

            if week_gap > 2:
                continue

            generated.extend(
                compare_weekly_records(previous, current)
            )

    return generated

def generate_rolling_baseline_signals(
    records: list[dict[str, Any]],
    window: int = 3,
    include_postseason: bool = False,
) -> list[dict[str, Any]]:
    """
    Compare each player appearance against prior appearances.

    A signal is generated only when:
        - at least `window` prior appearances exist;
        - the metric exceeds its configured minimum delta;
        - the comparison stays within the same season.
    """
    if window < 1:
        raise ValueError("window must be at least 1")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        player_key = _player_key(record)

        if not player_key:
            continue

        grouped[player_key].append(record)

    generated: list[dict[str, Any]] = []

    for player_records in grouped.values():
        ordered = sorted(
            player_records,
            key=lambda item: (
                item.get("season") or 0,
                item.get("week") or 0,
            ),
        )

        for index, current in enumerate(ordered):
            if index < window:
                continue

            current_season = current.get("season")
            prior_records = ordered[index - window:index]

            if any(
                record.get("season") != current_season
                for record in prior_records
            ):
                continue

            current_stats = _statistics(current)
            player_id = _player_key(current)
            player_name = _player_name(current)

            team = str(
                current.get("team")
                or current.get("recent_team")
                or ""
            )

            position = str(
                current.get("position")
                or current.get("position_group")
                or ""
            )

            current_week = current.get("week")

            if (
                not include_postseason
                and isinstance(current_week, int)
                and current_week > 18
            ):
                continue

            for metric, rule in METRIC_RULES.items():
                previous_values = [
                    _number(_statistics(record).get(metric))
                    for record in prior_records
                ]

                baseline = sum(previous_values) / len(previous_values)
                current_value = _number(current_stats.get(metric))
                delta = current_value - baseline

                # Position-specific thresholds
                if metric == "carries" and position.upper() == "QB":
                    minimum_delta = 6.0
                    weight = 0.06
                else:
                    minimum_delta = rule["minimum_delta"]
                    weight = rule["weight"]

                if abs(delta) < minimum_delta:
                    continue

                direction = (
                    "above"
                    if delta > 0
                    else "below"
                )

                sentiment = (
                    "positive"
                    if delta > 0
                    else "negative"
                )

                impact_score = round(
                    max(
                        -1.0,
                        min(
                            1.0,
                            delta * weight,
                        ),
                    ),
                    3,
                )

                percent_change = None

                if baseline != 0:
                    percent_change = round(
                        (delta / abs(baseline)) * 100,
                        1,
                    )

                confidence = (
                    0.94
                    if rule["signal_type"] == "opportunity"
                    else 0.78
                )

                change_text= _format_change(
                    baseline,
                    delta,
                    percent_change,
                )

                reason = (
                    f"{rule['label']} were {direction} the "
                    f"previous {window}-game average: "
                    f"{current_value:g} versus {baseline:.1f} "
                    f"({change_text}) in Week {current_week}."
                )

                generated.append(
                    {
                        "source": "nflverse",
                        "signal_type": rule["signal_type"],
                        "signal_method": "rolling_baseline",
                        "metric": metric,
                        "player_id": player_id,
                        "player_name": player_name,
                        "team": team,
                        "position": position,
                        "season": current_season,
                        "current_week": current_week,
                        "baseline_window": window,
                        "baseline_value": round(baseline, 3),
                        "current_value": current_value,
                        "delta": round(delta, 3),
                        "percent_change": percent_change,
                        "direction": direction,
                        "sentiment": sentiment,
                        "impact_score": impact_score,
                        "confidence": confidence,
                        "reason": reason,
                    }
                )

    return generated

def _format_change(
    baseline: float,
    delta: float,
    percent_change: float | None,
) -> str:
    """Format changes without exaggerating very small baselines."""
    if baseline < 3 or percent_change is None:
        return f"{delta:+.1f}"

    return f"{percent_change:+.1f}%"

def test_low_baseline_uses_absolute_change_text():
    records = [
        {
            "player_id": "P001",
            "player_name": "Low Volume Receiver",
            "position": "WR",
            "season": 2025,
            "week": 1,
            "statistics": {"targets": 1},
        },
        {
            "player_id": "P001",
            "player_name": "Low Volume Receiver",
            "position": "WR",
            "season": 2025,
            "week": 2,
            "statistics": {"targets": 1},
        },
        {
            "player_id": "P001",
            "player_name": "Low Volume Receiver",
            "position": "WR",
            "season": 2025,
            "week": 3,
            "statistics": {"targets": 1},
        },
        {
            "player_id": "P001",
            "player_name": "Low Volume Receiver",
            "position": "WR",
            "season": 2025,
            "week": 4,
            "statistics": {"targets": 5},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert "(+4.0)" in signals[0]["reason"]
    assert "+400.0%" not in signals[0]["reason"]


def test_qb_small_carry_change_is_ignored():
    records = [
        {
            "player_id": "QB1",
            "player_name": "Test Quarterback",
            "position": "QB",
            "season": 2025,
            "week": 1,
            "statistics": {"carries": 1},
        },
        {
            "player_id": "QB1",
            "player_name": "Test Quarterback",
            "position": "QB",
            "season": 2025,
            "week": 2,
            "statistics": {"carries": 1},
        },
        {
            "player_id": "QB1",
            "player_name": "Test Quarterback",
            "position": "QB",
            "season": 2025,
            "week": 3,
            "statistics": {"carries": 1},
        },
        {
            "player_id": "QB1",
            "player_name": "Test Quarterback",
            "position": "QB",
            "season": 2025,
            "week": 4,
            "statistics": {"carries": 5},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert signals == []


def test_postseason_is_excluded_by_default():
    records = [
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "position": "WR",
            "season": 2025,
            "week": 16,
            "statistics": {"targets": 4},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "position": "WR",
            "season": 2025,
            "week": 17,
            "statistics": {"targets": 4},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "position": "WR",
            "season": 2025,
            "week": 18,
            "statistics": {"targets": 4},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "position": "WR",
            "season": 2025,
            "week": 19,
            "statistics": {"targets": 12},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert signals == []
