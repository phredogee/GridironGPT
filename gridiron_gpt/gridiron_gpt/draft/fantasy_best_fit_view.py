from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from gridiron_gpt.draft.fantasy_best_fit_service import FantasyBestFitService
from gridiron_gpt.draft.fantasy_position_scarcity_service import (
    FantasyPositionScarcityService,
)


@dataclass(frozen=True)
class BestFitView:
    score: object
    fit_score: float
    roster_need: bool
    draft_value: float
    scarcity_level: str
    scarcity_bonus: float
    reason: str


def build_best_fit_views(
    candidates: Iterable[object],
    roster_scores: Iterable[object],
    market_views: Mapping[str, object],
    *,
    limit: int = 5,
) -> list[BestFitView]:
    candidate_list = list(candidates)
    scarcity_service = FantasyPositionScarcityService()
    scarcity_views = {
        str(candidate.player_id): scarcity_service.evaluate(candidate, candidate_list)
        for candidate in candidate_list
        if getattr(candidate, "tier", None) is not None
    }

    recommendations = FantasyBestFitService().recommend(
        candidate_list,
        roster_scores,
        market_views,
        scarcity_views=scarcity_views,
        limit=limit,
    )
    views: list[BestFitView] = []
    for recommendation in recommendations:
        reasons: list[str] = []
        if recommendation.roster_need:
            reasons.append("fills active roster need")
        if recommendation.draft_value > 0:
            reasons.append("positive draft value")

        scarcity_view = scarcity_views.get(
            str(getattr(recommendation.score, "player_id", ""))
        )
        if (
            scarcity_view is not None
            and recommendation.scarcity_level in {"medium", "high"}
        ):
            scarcity_reason = f"{recommendation.scarcity_level} position scarcity"
            if scarcity_view.score_drop > 0:
                scarcity_reason += f" · {scarcity_view.score_drop:.1f}-point drop"
            if scarcity_view.tier_cliff:
                scarcity_reason += " across tier boundary"
            reasons.append(scarcity_reason)

        if not reasons:
            reasons.append("strong board position")
        views.append(
            BestFitView(
                score=recommendation.score,
                fit_score=recommendation.fit_score,
                roster_need=recommendation.roster_need,
                draft_value=recommendation.draft_value,
                scarcity_level=recommendation.scarcity_level,
                scarcity_bonus=recommendation.scarcity_bonus,
                reason=" · ".join(reasons),
            )
        )
    return views
