from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median

from gridiron_gpt.draft.consensus_adp_service import ConsensusAdpRecord, ConsensusAdpService
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore


@dataclass(frozen=True)
class FantasyRankingMarketView:
    player_id: str
    overall_rank: int
    position_rank: int
    tier: int
    consensus_adp: float | None
    adp_source_count: int
    adp_spread: float | None
    draft_value: float | None
    source_adps: dict[str, float] = field(default_factory=dict)


class FantasyRankingTierService:
    """Add position rank, score-gap tiers, and rank-vs-market value metadata."""

    def __init__(self, *, minimum_tier_gap: float = 2.5) -> None:
        if minimum_tier_gap <= 0:
            raise ValueError("minimum_tier_gap must be positive")
        self.minimum_tier_gap = float(minimum_tier_gap)

    def build(
        self,
        scores: list[FantasyRankingScore],
        *,
        consensus_adp_by_key: dict[str, ConsensusAdpRecord] | None = None,
    ) -> dict[str, FantasyRankingMarketView]:
        consensus_adp_by_key = consensus_adp_by_key or {}
        overall_rank = {score.player_id: rank for rank, score in enumerate(scores, start=1)}
        views: dict[str, FantasyRankingMarketView] = {}

        positions = sorted({(score.position or "").upper() for score in scores if score.position})
        for position in positions:
            position_scores = [
                score for score in scores if (score.position or "").upper() == position
            ]
            threshold = self._tier_threshold(position_scores)
            tier = 1
            previous_score: float | None = None

            for position_rank, score in enumerate(position_scores, start=1):
                if previous_score is not None:
                    gap = previous_score - score.ranking_score
                    if gap >= threshold:
                        tier += 1
                previous_score = score.ranking_score

                market = consensus_adp_by_key.get(
                    ConsensusAdpService.name_key(score.player_name)
                )
                consensus_adp = market.consensus_adp if market else None
                rank = overall_rank[score.player_id]
                draft_value = (
                    round(consensus_adp - rank, 2)
                    if consensus_adp is not None
                    else None
                )
                source_count = market.source_count if market else 0
                views[score.player_id] = FantasyRankingMarketView(
                    player_id=score.player_id,
                    overall_rank=rank,
                    position_rank=position_rank,
                    tier=tier,
                    consensus_adp=consensus_adp,
                    adp_source_count=source_count,
                    adp_spread=(
                        market.adp_spread
                        if market is not None and source_count >= 2
                        else None
                    ),
                    draft_value=draft_value,
                    source_adps=dict(market.source_values) if market else {},
                )

        return views

    def _tier_threshold(self, scores: list[FantasyRankingScore]) -> float:
        if len(scores) < 3:
            return self.minimum_tier_gap
        gaps = [
            scores[index - 1].ranking_score - scores[index].ranking_score
            for index in range(1, len(scores))
        ]
        center = median(gaps)
        deviations = [abs(gap - center) for gap in gaps]
        mad = median(deviations)
        return max(self.minimum_tier_gap, float(center + (1.5 * mad)))
