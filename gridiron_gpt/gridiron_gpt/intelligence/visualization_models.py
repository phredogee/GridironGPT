from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BarDatum:
    label: str
    value: float


@dataclass(frozen=True)
class TimelineDatum:
    label: str
    headline: str
    impact: str
    value: float
    cumulative_score: float
    source: str


def build_signal_breakdown(signals: Iterable[dict]) -> list[BarDatum]:
    """Return chart-ready signal contributions, strongest first."""
    rows = [
        BarDatum(
            label=str(signal.get("headline") or "Untitled signal"),
            value=round(float(signal.get("value") or 0.0), 3),
        )
        for signal in signals
    ]
    return sorted(rows, key=lambda row: abs(row.value), reverse=True)


def build_cortex_timeline(signals: Iterable[dict]) -> list[TimelineDatum]:
    """Build a chronological event timeline with a running Cortex score."""
    ordered = sorted(
        signals,
        key=lambda signal: str(signal.get("date") or signal.get("event_date") or ""),
    )
    cumulative = 0.0
    rows: list[TimelineDatum] = []
    for signal in ordered:
        value = float(signal.get("value") or 0.0)
        cumulative += value
        rows.append(
            TimelineDatum(
                label=str(signal.get("date") or signal.get("event_date") or "Unknown date"),
                headline=str(signal.get("headline") or "Untitled signal"),
                impact=str(signal.get("impact") or "unknown"),
                value=round(value, 3),
                cumulative_score=round(cumulative, 3),
                source=str(signal.get("source") or "Unknown source"),
            )
        )
    return rows


def recommendation_distribution(scores: dict) -> list[BarDatum]:
    from gridiron_gpt.data_ingest.player_scores import recommendation_from_score

    counts = Counter(
        recommendation_from_score(float(data.get("adjusted_score", data.get("score", 0.0))))
        for data in scores.values()
        if float(data.get("adjusted_score", data.get("score", 0.0))) != 0.0
    )
    order = ("BUY", "WATCH", "HOLD", "MONITOR", "SELL")
    return [BarDatum(label=label, value=float(counts[label])) for label in order]


def team_momentum(scores: dict) -> list[BarDatum]:
    totals: dict[str, float] = defaultdict(float)
    for (_player, team), data in scores.items():
        totals[str(team or "UNK")] += float(
            data.get("adjusted_score", data.get("score", 0.0))
        )
    rows = [BarDatum(label=team, value=round(value, 3)) for team, value in totals.items()]
    return sorted(rows, key=lambda row: row.value, reverse=True)


def position_rankings(scores: dict, positions: dict[str, str]) -> dict[str, list[BarDatum]]:
    grouped: dict[str, list[BarDatum]] = defaultdict(list)
    for (player, _team), data in scores.items():
        position = str(positions.get(player, "UNK")).upper()
        grouped[position].append(
            BarDatum(
                label=player,
                value=round(float(data.get("adjusted_score", data.get("score", 0.0))), 3),
            )
        )
    return {
        position: sorted(rows, key=lambda row: row.value, reverse=True)
        for position, rows in grouped.items()
    }


def confidence_components(signals: Iterable[dict]) -> dict[str, float]:
    rows = list(signals)
    if not rows:
        return {"agreement": 0.0, "positive_share": 0.0, "negative_share": 0.0}
    positive = sum(float(row.get("value") or 0.0) > 0 for row in rows)
    negative = sum(float(row.get("value") or 0.0) < 0 for row in rows)
    total = len(rows)
    return {
        "agreement": round(max(positive, negative) / total, 3),
        "positive_share": round(positive / total, 3),
        "negative_share": round(negative / total, 3),
    }
