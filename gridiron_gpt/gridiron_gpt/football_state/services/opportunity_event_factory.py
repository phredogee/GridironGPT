from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)


class OpportunityEventFactory:
    """Convert derived teammate opportunity changes into Cortex evidence."""

    SOURCE = "canonical roster opportunity"

    def build_event(self, change: OpportunityChange) -> RawEvent:
        increased = change.direction == OpportunityDirection.INCREASED
        sentiment = "positive" if increased else "negative"
        signed_impact = change.magnitude if increased else -change.magnitude

        return RawEvent(
            source=self.SOURCE,
            headline=(
                f"{change.affected_player_name} opportunity {change.direction.value} "
                f"after roster change involving {change.source_player_name}"
            ),
            player=change.affected_player_name,
            player_id=change.affected_player_id,
            event_type="roster_opportunity",
            sentiment=sentiment,
            impact_score=signed_impact,
            confidence=0.9,
            evidence={
                "source_id": self._source_id(change),
                "roster_opportunity": {
                    "source_player_id": change.source_player_id,
                    "source_player_name": change.source_player_name,
                    "relationship_type": change.relationship_type,
                    "direction": change.direction.value,
                    "magnitude": change.magnitude,
                    "reason": change.reason,
                },
            },
        )

    @staticmethod
    def _source_id(change: OpportunityChange) -> str:
        return ":".join(
            [
                "roster_opportunity",
                change.source_player_id,
                change.affected_player_id,
                change.relationship_type,
                change.direction.value,
                f"{change.magnitude:.6f}",
            ]
        )
