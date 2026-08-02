from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gridiron_cortex.models.raw_event import RawEvent


@dataclass(frozen=True)
class StatisticalInterpretation:
    sentiment: str
    impact_score: float
    confidence: float
    indicators: dict[str, float]
    reasons: list[str]


class StatisticalEventInterpreter:
    """Interpret structured player-stat evidence without headline sentiment."""

    DATASET = "player_stats"

    def can_interpret(self, event: RawEvent) -> bool:
        metadata = event.evidence.get("source_metadata") or {}
        return (
            metadata.get("provider") == "nflverse"
            and metadata.get("dataset") == self.DATASET
            and isinstance(metadata.get("stats"), dict)
        )

    def interpret(self, event: RawEvent) -> StatisticalInterpretation:
        metadata = event.evidence.get("source_metadata") or {}
        stats = metadata.get("stats") or {}
        position = (event.position or "").upper()

        indicators = self._indicators(position, stats)
        impact = self._impact(position, indicators)

        if impact > 0.15:
            sentiment = "positive"
        elif impact < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        observed = sum(
            1 for value in indicators.values()
            if value != 0.0
        )
        confidence = min(0.9, 0.55 + (0.07 * observed))

        return StatisticalInterpretation(
            sentiment=sentiment,
            impact_score=round(impact, 3),
            confidence=round(confidence, 3),
            indicators=indicators,
            reasons=self._reasons(position, indicators),
        )

    @classmethod
    def _indicators(
        cls,
        position: str,
        stats: dict[str, Any],
    ) -> dict[str, float]:
        targets = cls._number(stats, "targets")
        carries = cls._number(stats, "carries", "rushing_attempts")
        receptions = cls._number(stats, "receptions")
        receiving_yards = cls._number(stats, "receiving_yards")
        rushing_yards = cls._number(stats, "rushing_yards")
        passing_yards = cls._number(stats, "passing_yards")
        passing_tds = cls._number(stats, "passing_tds", "passing_touchdowns")
        rushing_tds = cls._number(stats, "rushing_tds", "rushing_touchdowns")
        receiving_tds = cls._number(stats, "receiving_tds", "receiving_touchdowns")
        interceptions = cls._number(stats, "interceptions", "passing_interceptions")
        sacks = cls._number(stats, "sacks", "sacks_suffered")

        return {
            "targets": targets,
            "carries": carries,
            "receptions": receptions,
            "touches": carries + receptions,
            "receiving_yards": receiving_yards,
            "rushing_yards": rushing_yards,
            "passing_yards": passing_yards,
            "touchdowns": passing_tds + rushing_tds + receiving_tds,
            "turnovers": interceptions,
            "sacks": sacks,
        }

    @staticmethod
    def _impact(
        position: str,
        values: dict[str, float],
    ) -> float:
        if position == "QB":
            score = (
                min(values["passing_yards"] / 300.0, 1.0) * 0.35
                + min(values["touchdowns"] / 3.0, 1.0) * 0.4
                + min(values["rushing_yards"] / 50.0, 1.0) * 0.15
                - min(values["turnovers"] / 3.0, 1.0) * 0.35
                - min(values["sacks"] / 5.0, 1.0) * 0.1
            )
        else:
            score = (
                min(values["touches"] / 20.0, 1.0) * 0.35
                + min(values["targets"] / 10.0, 1.0) * 0.2
                + min(
                    (values["rushing_yards"] + values["receiving_yards"])
                    / 120.0,
                    1.0,
                ) * 0.25
                + min(values["touchdowns"] / 2.0, 1.0) * 0.2
            )

        return max(-1.0, min(score, 1.0))

    @staticmethod
    def _reasons(
        position: str,
        values: dict[str, float],
    ) -> list[str]:
        reasons = []

        if position == "QB":
            if values["passing_yards"]:
                reasons.append(
                    f"{int(values['passing_yards'])} passing yards"
                )
            if values["touchdowns"]:
                reasons.append(
                    f"{int(values['touchdowns'])} total touchdowns"
                )
            if values["turnovers"]:
                reasons.append(
                    f"{int(values['turnovers'])} interceptions"
                )
        else:
            if values["touches"]:
                reasons.append(f"{int(values['touches'])} touches")
            if values["targets"]:
                reasons.append(f"{int(values['targets'])} targets")
            scrimmage = values["rushing_yards"] + values["receiving_yards"]
            if scrimmage:
                reasons.append(f"{int(scrimmage)} scrimmage yards")
            if values["touchdowns"]:
                reasons.append(
                    f"{int(values['touchdowns'])} total touchdowns"
                )

        return reasons or ["Structured weekly statistical evidence"]

    @staticmethod
    def _number(stats: dict[str, Any], *keys: str) -> float:
        for key in keys:
            value = stats.get(key)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return 0.0
