from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WaitRiskResult:
    player_id: str
    ranking_score: float
    current_pick: int
    next_pick: int
    picks_until_next_turn: int
    consensus_adp: float | None
    market_gap: float | None
    risk_level: str
    recommendation: str
    reason: str


class FantasyWaitRiskService:
    """Estimate market-based risk of waiting until the user's next pick.

    This service is advisory only. It reads the authoritative production ranking
    score but never changes it. Positive market_gap means consensus ADP falls
    before the user's next pick; negative means ADP falls after it.
    """

    def evaluate(
        self,
        player: object,
        *,
        current_pick: int,
        next_pick: int,
        consensus_adp: float | None,
    ) -> WaitRiskResult:
        player_id = str(getattr(player, "player_id", ""))
        ranking_score = float(getattr(player, "ranking_score", 0.0))
        picks_until_next_turn = max(0, int(next_pick) - int(current_pick))

        if consensus_adp is None:
            return WaitRiskResult(
                player_id=player_id,
                ranking_score=ranking_score,
                current_pick=int(current_pick),
                next_pick=int(next_pick),
                picks_until_next_turn=picks_until_next_turn,
                consensus_adp=None,
                market_gap=None,
                risk_level="unknown",
                recommendation="unknown",
                reason="Wait risk unknown: consensus ADP is unavailable.",
            )

        adp = float(consensus_adp)
        market_gap = round(float(next_pick) - adp, 1)

        if market_gap >= 3.0:
            risk_level = "high"
            recommendation = "unlikely_available"
            reason = (
                f"High wait risk: consensus ADP {adp:.1f} is {market_gap:.1f} picks "
                f"before your next pick at {int(next_pick)}."
            )
        elif market_gap <= -3.0:
            risk_level = "low"
            recommendation = "likely_available"
            reason = (
                f"Low wait risk: consensus ADP {adp:.1f} is {abs(market_gap):.1f} picks "
                f"after your next pick at {int(next_pick)}."
            )
        else:
            risk_level = "medium"
            recommendation = "uncertain"
            reason = (
                f"Medium wait risk: consensus ADP {adp:.1f} is close to your next "
                f"pick at {int(next_pick)}."
            )

        return WaitRiskResult(
            player_id=player_id,
            ranking_score=ranking_score,
            current_pick=int(current_pick),
            next_pick=int(next_pick),
            picks_until_next_turn=picks_until_next_turn,
            consensus_adp=adp,
            market_gap=market_gap,
            risk_level=risk_level,
            recommendation=recommendation,
            reason=reason,
        )
