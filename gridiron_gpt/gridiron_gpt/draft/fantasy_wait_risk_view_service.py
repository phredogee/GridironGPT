from __future__ import annotations

from gridiron_gpt.draft.fantasy_draft_turn_service import FantasyDraftTurnService
from gridiron_gpt.draft.fantasy_wait_risk_service import (
    FantasyWaitRiskService,
    WaitRiskResult,
)


class FantasyWaitRiskViewService:
    """Adapt live draft state and market data into deterministic wait-risk guidance."""

    def __init__(self, *, league_size: int, draft_slot: int) -> None:
        self.turn_service = FantasyDraftTurnService(
            league_size=league_size,
            draft_slot=draft_slot,
        )
        self.wait_risk_service = FantasyWaitRiskService()

    def evaluate(
        self,
        player: object,
        market_view: object | None,
        *,
        drafted_count: int,
    ) -> WaitRiskResult:
        current_pick = self.turn_service.current_pick(drafted_count=drafted_count)
        next_pick = self.turn_service.next_pick_after(current_pick)
        consensus_adp = (
            getattr(market_view, "consensus_adp", None)
            if market_view is not None
            else None
        )

        return self.wait_risk_service.evaluate(
            player,
            current_pick=current_pick,
            next_pick=next_pick,
            consensus_adp=consensus_adp,
        )
