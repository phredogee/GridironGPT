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
    is_user_turn: bool
    context_label: str
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

    is_user_turn = result.current_pick == result.next_pick - result.picks_until_next_turn and result.current_pick == (
        settings.draft_slot
        if result.current_pick <= settings.league_size
        else result.current_pick
    )

    # A turn is more reliably identified by whether the current overall pick is
    # one of the user's snake-draft selections.
    turn_service = FantasyWaitRiskViewService(
        league_size=settings.league_size,
        draft_slot=settings.draft_slot,
    ).turn_service
    is_user_turn = turn_service.next_pick_after(result.current_pick - 1) == result.current_pick

    if is_user_turn:
        context_label = (
            f"Current Pick {result.current_pick} · You are on the clock · Next Pick {result.next_pick}"
        )
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
    else:
        context_label = f"Current Pick {result.current_pick} · Your Upcoming Pick {result.next_pick}"
        risk_labels = {
            "high": f"AVAILABILITY AT PICK {result.next_pick} · HIGH RISK",
            "medium": f"AVAILABILITY AT PICK {result.next_pick} · MEDIUM RISK",
            "low": f"AVAILABILITY AT PICK {result.next_pick} · LOW RISK",
            "unknown": f"AVAILABILITY AT PICK {result.next_pick} · UNKNOWN",
        }
        recommendation_labels = {
            "unlikely_available": "unlikely to reach your pick",
            "uncertain": "uncertain to reach your pick",
            "likely_available": "likely to reach your pick",
            "unknown": "availability at your pick unknown",
        }

    return WaitRiskDisplay(
        player_id=result.player_id,
        ranking_score=result.ranking_score,
        current_pick=result.current_pick,
        next_pick=result.next_pick,
        is_user_turn=is_user_turn,
        context_label=context_label,
        risk_label=risk_labels[result.risk_level],
        recommendation_label=recommendation_labels[result.recommendation],
        reason=result.reason,
    )
