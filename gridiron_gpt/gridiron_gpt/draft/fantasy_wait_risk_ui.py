from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_draft_settings import FantasyDraftSettings
from gridiron_gpt.draft.fantasy_wait_risk_view_service import FantasyWaitRiskViewService


@dataclass(frozen=True)
class WaitRiskDisplay:
    player_id: str
    ranking_score: float
    current_pick: int
    next_pick: int
    risk_label: str
    recommendation_label: str
    reason: str


def build_wait_risk_display(
    *,
    player_id: str,
    ranking_score: float,
    consensus_adp: float | None,
    drafted_count: int,
    settings: FantasyDraftSettings,
) -> WaitRiskDisplay:
    player = SimpleNamespace(player_id=player_id, ranking_score=ranking_score)
    market_view = SimpleNamespace(consensus_adp=consensus_adp)
    result = FantasyWaitRiskViewService(
        league_size=settings.league_size,
        draft_slot=settings.draft_slot,
    ).evaluate(player, market_view, drafted_count=drafted_count)

    risk_labels = {
        "high": "HIGH WAIT RISK",
        "medium": "MEDIUM WAIT RISK",
        "low": "LOW WAIT RISK",
        "unknown": "WAIT RISK UNKNOWN",
    }
    recommendation_labels = {
        "unlikely_available": f"unlikely to reach Pick {result.next_pick}",
        "uncertain": f"uncertain to reach Pick {result.next_pick}",
        "likely_available": f"likely to reach Pick {result.next_pick}",
        "unknown": "next-pick availability unknown",
    }

    return WaitRiskDisplay(
        player_id=result.player_id,
        ranking_score=result.ranking_score,
        current_pick=result.current_pick,
        next_pick=result.next_pick,
        risk_label=risk_labels[result.risk_level],
        recommendation_label=recommendation_labels[result.recommendation],
        reason=result.reason,
    )
