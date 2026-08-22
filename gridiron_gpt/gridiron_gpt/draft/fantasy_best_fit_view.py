from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_gpt.draft.fantasy_best_fit_service import FantasyBestFitService


@dataclass(frozen=True)
class BestFitView:
    score: object
    fit_score: float
    roster_need: bool
    draft_value: float
    reason: str


def build_best_fit_views(
    candidates: Iterable[object],
    roster_scores: Iterable[object],
    market_views: Mapping[str, object],
    *,
    limit: int = 5,
) -> list[BestFitView]:
    recommendations = FantasyBestFitService().recommend(
        candidates,
        roster_scores,
        market_views,
        limit=limit,
    )
    views: list[BestFitView] = []
    for recommendation in recommendations:
        reasons: list[str] = []
        if recommendation.roster_need:
            reasons.append("fills active roster need")
        if recommendation.draft_value > 0:
            reasons.append("positive draft value")
        if not reasons:
            reasons.append("strong board position")
        views.append(
            BestFitView(
                score=recommendation.score,
                fit_score=recommendation.fit_score,
                roster_need=recommendation.roster_need,
                draft_value=recommendation.draft_value,
                reason=" · ".join(reasons),
            )
        )
    return views
