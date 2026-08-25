from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class PositionScarcityResult:
    player_id: str
    position: str
    current_score: float
    next_score: float | None
    score_drop: float
    current_tier: int | None
    next_tier: int | None
    tier_cliff: bool
    remaining_same_position: int
    scarcity_level: str
    reason: str


class FantasyPositionScarcityService:
    """Evaluate the cost of passing on a player at a given position.

    This service is advisory only. It reads ranking information from the
    supplied player objects and never mutates production ranking scores.
    """

    HIGH_DROP_THRESHOLD = 7.0
    MEDIUM_DROP_THRESHOLD = 3.0

    def evaluate(
        self,
        candidate: Any,
        available_players: Sequence[Any],
    ) -> PositionScarcityResult:
        position = str(candidate.position).upper()
        candidate_id = str(candidate.player_id)
        current_score = float(candidate.ranking_score)
        current_tier = getattr(candidate, "tier", None)

        alternatives = [
            player
            for player in available_players
            if str(getattr(player, "player_id", "")) != candidate_id
            and str(getattr(player, "position", "")).upper() == position
        ]
        alternatives.sort(
            key=lambda player: float(player.ranking_score),
            reverse=True,
        )

        next_player = alternatives[0] if alternatives else None
        next_score = (
            float(next_player.ranking_score)
            if next_player is not None
            else None
        )
        next_tier = (
            getattr(next_player, "tier", None)
            if next_player is not None
            else None
        )

        score_drop = (
            max(0.0, current_score - next_score)
            if next_score is not None
            else current_score
        )
        tier_cliff = (
            current_tier is not None
            and next_tier is not None
            and next_tier > current_tier
        )

        scarcity_level = self._scarcity_level(
            score_drop=score_drop,
            tier_cliff=tier_cliff,
            remaining=len(alternatives),
        )

        return PositionScarcityResult(
            player_id=candidate_id,
            position=position,
            current_score=current_score,
            next_score=next_score,
            score_drop=score_drop,
            current_tier=current_tier,
            next_tier=next_tier,
            tier_cliff=tier_cliff,
            remaining_same_position=len(alternatives),
            scarcity_level=scarcity_level,
            reason=self._reason(
                scarcity_level,
                score_drop,
                tier_cliff,
                len(alternatives),
            ),
        )

    def _scarcity_level(
        self,
        *,
        score_drop: float,
        tier_cliff: bool,
        remaining: int,
    ) -> str:
        if remaining == 0 or score_drop >= self.HIGH_DROP_THRESHOLD:
            return "high"
        if tier_cliff or score_drop >= self.MEDIUM_DROP_THRESHOLD:
            return "medium"
        return "low"

    @staticmethod
    def _reason(
        scarcity_level: str,
        score_drop: float,
        tier_cliff: bool,
        remaining: int,
    ) -> str:
        details = [
            f"{remaining} same-position alternatives remain",
            f"next-option score drop is {score_drop:.1f}",
        ]
        if tier_cliff:
            details.append("the next option crosses a tier boundary")
        return f"{scarcity_level.capitalize()} scarcity: " + "; ".join(details) + "."
