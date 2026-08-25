from dataclasses import dataclass
from typing import Any

from gridiron_gpt.draft.fantasy_position_scarcity_service import (
    PositionScarcityResult,
)


@dataclass(frozen=True)
class PickTimingResult:
    player_id: str
    position: str
    decision: str
    urgency: str
    ranking_score: float
    score_drop: float
    tier_cliff: bool
    roster_need: bool
    reason: str


class FantasyPickTimingService:
    """Advise whether to take a candidate now or whether waiting is reasonable.

    This is a deterministic advisory layer. It consumes existing ranking and
    scarcity information and never mutates the candidate's ranking score.
    """

    def evaluate(
        self,
        candidate: Any,
        *,
        scarcity: PositionScarcityResult,
        roster_need: bool,
    ) -> PickTimingResult:
        urgency = scarcity.scarcity_level
        score_drop = round(float(scarcity.score_drop), 3)

        if urgency == "high":
            decision = "take_now"
            reason = self._take_now_reason(scarcity, roster_need)
        elif urgency == "medium" and roster_need:
            decision = "take_now"
            reason = (
                "Take now: medium position scarcity combines with an active "
                "roster need; waiting risks a "
                f"{score_drop:.1f}-point drop."
            )
        elif urgency == "low":
            decision = "can_wait"
            reason = (
                "Can wait: comparable same-position options remain and the "
                f"next-option score drop is only {score_drop:.1f}."
            )
        else:
            decision = "neutral"
            reason = (
                "Neutral timing: some position pressure exists, but current "
                "evidence is not strong enough to recommend reaching now."
            )

        return PickTimingResult(
            player_id=str(candidate.player_id),
            position=str(candidate.position).upper(),
            decision=decision,
            urgency=urgency,
            ranking_score=float(candidate.ranking_score),
            score_drop=score_drop,
            tier_cliff=scarcity.tier_cliff,
            roster_need=roster_need,
            reason=reason,
        )

    @staticmethod
    def _take_now_reason(
        scarcity: PositionScarcityResult,
        roster_need: bool,
    ) -> str:
        details = ["Take now: high position scarcity"]

        if scarcity.remaining_same_position == 0:
            details.append("no same-position alternatives remain")
        else:
            details.append(
                f"waiting exposes a {float(scarcity.score_drop):.1f}-point drop"
            )

        if scarcity.tier_cliff:
            details.append("the next option crosses a tier boundary")
        if roster_need:
            details.append("the player also fills an active roster need")
        return "; ".join(details) + "."
