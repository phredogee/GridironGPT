from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_gpt.draft.fantasy_roster_advice_service import FantasyRosterAdviceService


@dataclass(frozen=True)
class BestFitRecommendation:
    score: object
    fit_score: float
    roster_need: bool
    draft_value: float


class FantasyBestFitService:
    """Rank available candidates for advisory use without changing production rankings."""

    def __init__(self, roster_advice_service: FantasyRosterAdviceService | None = None):
        self.roster_advice_service = roster_advice_service or FantasyRosterAdviceService()

    def recommend(
        self,
        candidates: Iterable[object],
        roster_scores: Iterable[object],
        market_views: Mapping[str, object],
        *,
        limit: int = 5,
    ) -> list[BestFitRecommendation]:
        if limit <= 0:
            return []

        advice = self.roster_advice_service.build(roster_scores)
        recommendations: list[BestFitRecommendation] = []

        for candidate in candidates:
            player_id = str(getattr(candidate, "player_id", ""))
            position = str(getattr(candidate, "position", "") or "").upper()
            ranking_score = float(getattr(candidate, "ranking_score", 0.0) or 0.0)
            market_view = market_views.get(player_id)
            draft_value = float(getattr(market_view, "draft_value", 0.0) or 0.0) if market_view is not None else 0.0

            need = advice.needs.get(position)
            fills_need = bool(need is not None and not need.filled)

            # Advisory-only blend. Production ranking_score is read, never mutated.
            # Ranking quality remains dominant; active roster need and positive
            # market value provide modest contextual bonuses.
            need_bonus = 8.0 if fills_need else 0.0
            value_bonus = max(-5.0, min(5.0, draft_value * 0.25))
            fit_score = ranking_score + need_bonus + value_bonus

            recommendations.append(
                BestFitRecommendation(
                    score=candidate,
                    fit_score=fit_score,
                    roster_need=fills_need,
                    draft_value=draft_value,
                )
            )

        recommendations.sort(
            key=lambda item: (
                -item.fit_score,
                -float(getattr(item.score, "ranking_score", 0.0) or 0.0),
                str(getattr(item.score, "player_name", "")),
            )
        )
        return recommendations[:limit]
