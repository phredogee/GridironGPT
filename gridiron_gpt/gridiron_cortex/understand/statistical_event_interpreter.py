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
    context: dict[str, Any]


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
        context = metadata.get("stat_context") or {}
        position = (event.position or "").upper()

        indicators = self._indicators(position, stats)
        base_impact = self._impact(position, indicators)
        trend_adjustment, trend_reasons = self._trend_adjustment(
            position=position,
            context=context,
        )
        impact = max(-1.0, min(base_impact + trend_adjustment, 1.0))

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
        prior_games = int(context.get("prior_games") or 0)
        confidence = min(
            0.95,
            0.55 + (0.07 * observed) + min(prior_games, 4) * 0.025,
        )

        reasons = self._reasons(position, indicators)
        reasons.extend(trend_reasons)

        enriched_context = dict(context)
        enriched_context["base_impact"] = round(base_impact, 3)
        enriched_context["trend_adjustment"] = round(trend_adjustment, 3)

        return StatisticalInterpretation(
            sentiment=sentiment,
            impact_score=round(impact, 3),
            confidence=round(confidence, 3),
            indicators=indicators,
            reasons=reasons,
            context=enriched_context,
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

    @classmethod
    def _trend_adjustment(
        cls,
        *,
        position: str,
        context: dict[str, Any],
    ) -> tuple[float, list[str]]:
        if int(context.get("prior_games") or 0) < 1:
            return 0.0, []

        deltas = context.get("deltas") or {}
        reasons: list[str] = []
        adjustment = 0.0

        if position == "QB":
            passing_delta = cls._number(deltas, "passing_yards")
            td_delta = cls._number(
                deltas,
                "passing_tds",
                "passing_touchdowns",
            )
            turnover_delta = cls._number(
                deltas,
                "interceptions",
                "passing_interceptions",
            )

            adjustment += max(-0.12, min(passing_delta / 1000.0, 0.12))
            adjustment += max(-0.12, min(td_delta * 0.06, 0.12))
            adjustment -= max(-0.12, min(turnover_delta * 0.06, 0.12))

            if abs(passing_delta) >= 40:
                direction = "above" if passing_delta > 0 else "below"
                reasons.append(
                    f"Passing yards {abs(int(passing_delta))} {direction} prior-week average"
                )
        else:
            touch_delta = cls._number(deltas, "touches")
            target_delta = cls._number(deltas, "targets")
            yard_delta = cls._number(deltas, "scrimmage_yards")

            adjustment += max(-0.15, min(touch_delta * 0.015, 0.15))
            adjustment += max(-0.1, min(target_delta * 0.02, 0.1))
            adjustment += max(-0.1, min(yard_delta / 500.0, 0.1))

            if abs(touch_delta) >= 3:
                direction = "above" if touch_delta > 0 else "below"
                reasons.append(
                    f"Touches {abs(round(touch_delta, 1))} {direction} prior-week average"
                )
            if abs(target_delta) >= 2:
                direction = "above" if target_delta > 0 else "below"
                reasons.append(
                    f"Targets {abs(round(target_delta, 1))} {direction} prior-week average"
                )
            if abs(yard_delta) >= 25:
                direction = "above" if yard_delta > 0 else "below"
                reasons.append(
                    f"Scrimmage yards {abs(int(yard_delta))} {direction} prior-week average"
                )

        return max(-0.3, min(adjustment, 0.3)), reasons

    @staticmethod
    def _reasons(
        position: str,
        values: dict[str, float],
    ) -> list[str]:
        reasons = []

        if position == "QB":
            if values["passing_yards"]:
                reasons.append(f"{int(values['passing_yards'])} passing yards")
            if values["touchdowns"]:
                reasons.append(f"{int(values['touchdowns'])} total touchdowns")
            if values["turnovers"]:
                reasons.append(f"{int(values['turnovers'])} interceptions")
        else:
            if values["touches"]:
                reasons.append(f"{int(values['touches'])} touches")
            if values["targets"]:
                reasons.append(f"{int(values['targets'])} targets")
            scrimmage = values["rushing_yards"] + values["receiving_yards"]
            if scrimmage:
                reasons.append(f"{int(scrimmage)} scrimmage yards")
            if values["touchdowns"]:
                reasons.append(f"{int(values['touchdowns'])} total touchdowns")

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
