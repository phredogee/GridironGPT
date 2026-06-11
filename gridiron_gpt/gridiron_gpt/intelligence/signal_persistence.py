from typing import Optional

from gridiron_gpt.intelligence.entity_relationships import propagate_impact
from gridiron_gpt.storage.propagated_signal_repository import (
    save_propagated_signal,
)
from gridiron_gpt.storage.signal_repository import save_signal


def process_signal(
    player: str,
    value: float,
    source: str,
    team: Optional[str] = None,
    position: Optional[str] = None,
    headline: Optional[str] = None,
    signal_type: Optional[str] = None,
    impact: Optional[str] = None,
    confidence: float = 1.0,
    article_id: Optional[int] = None,
    event_date: Optional[str] = None,
) -> dict:
    """
    Persist a direct signal and all related propagated impacts.
    """

    direct_signal = save_signal(
        player=player,
        team=team,
        position=position,
        source=source,
        headline=headline,
        signal_type=signal_type,
        impact=impact,
        value=value,
        confidence=confidence,
        article_id=article_id,
        event_date=event_date,
    )

    propagated_impacts = propagate_impact(player, value)

    saved_propagated = []

    for impact_result in propagated_impacts:
        saved = save_propagated_signal(
            source_signal_id=direct_signal["id"],
            source_player=impact_result["source"],
            target_player=impact_result["target"],
            relationship_type=impact_result["relationship_type"],
            base_value=impact_result["source_score"],
            propagated_value=impact_result["propagated_score"],
            confidence=impact_result.get("confidence", confidence),
        )

        saved_propagated.append(saved)

    return {
        "direct_signal": direct_signal,
        "propagated_signals": saved_propagated,
        "propagated_count": len(saved_propagated),
    }
