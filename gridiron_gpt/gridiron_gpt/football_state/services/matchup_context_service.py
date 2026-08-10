from __future__ import annotations

from statistics import mean

from gridiron_gpt.football_state.models.matchup_context import (
    MatchupContext,
    MatchupTendency,
    OpponentMetric,
)


class MatchupContextService:
    """Classify matchup tendency from normalized, provenance-bearing metrics."""

    FAVORABLE_THRESHOLD = 0.10
    UNFAVORABLE_THRESHOLD = -0.10

    def classify(
        self,
        *,
        team: str,
        opponent: str,
        position: str,
        season: int,
        week: int,
        metrics: list[OpponentMetric],
        source: str = "opponent matchup context",
        evidence: dict | None = None,
    ) -> MatchupContext:
        if not team.strip() or not opponent.strip():
            raise ValueError("team and opponent are required")
        if team == opponent:
            raise ValueError("team and opponent must differ")
        if not position.strip():
            raise ValueError("position is required")

        usable = [metric for metric in metrics if metric.sample_games > 0]
        if not usable:
            return MatchupContext(
                team=team,
                opponent=opponent,
                position=position,
                season=season,
                week=week,
                tendency=MatchupTendency.UNKNOWN,
                score=0.0,
                confidence=0.0,
                source=source,
                evidence=evidence or {},
                reason="no usable opponent metrics",
            )

        score = mean(metric.favorable_delta for metric in usable)
        tendency = self._tendency(score)
        sample_games = max(metric.sample_games for metric in usable)
        confidence = min(0.95, 0.45 + 0.05 * min(sample_games, 8) + 0.03 * min(len(usable), 3))

        strongest = sorted(usable, key=lambda metric: abs(metric.favorable_delta), reverse=True)[:3]
        reason = ", ".join(
            f"{metric.name} {metric.favorable_delta:+.1%} vs league average"
            for metric in strongest
        )

        return MatchupContext(
            team=team,
            opponent=opponent,
            position=position,
            season=season,
            week=week,
            tendency=tendency,
            score=score,
            confidence=round(confidence, 4),
            metrics=tuple(usable),
            reason=reason,
            source=source,
            evidence=evidence or {},
        )

    def _tendency(self, score: float) -> MatchupTendency:
        if score >= self.FAVORABLE_THRESHOLD:
            return MatchupTendency.FAVORABLE
        if score <= self.UNFAVORABLE_THRESHOLD:
            return MatchupTendency.UNFAVORABLE
        return MatchupTendency.NEUTRAL
