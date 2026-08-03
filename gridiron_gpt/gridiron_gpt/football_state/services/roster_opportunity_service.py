from __future__ import annotations

from gridiron_cortex.propagation.propagation_planner import PropagationPlanner
from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)


class RosterOpportunityService:
    """Translate roster-impact signals into teammate opportunity consequences."""

    OPPORTUNITY_RELATIONSHIPS = {
        "backs_up",
        "competes_with",
        "target_competitor",
        "depth_chart_competitor",
    }

    def __init__(self, propagation_planner: PropagationPlanner) -> None:
        self.propagation_planner = propagation_planner

    def derive(
        self,
        *,
        source_player_id: str,
        source_player_name: str,
        source_impact_score: float,
    ) -> list[OpportunityChange]:
        if source_impact_score == 0:
            return []

        candidates = self.propagation_planner.plan(
            source_entity_id=source_player_id,
            max_depth=1,
            source_impact_score=source_impact_score,
        )

        changes: list[OpportunityChange] = []
        for candidate in candidates:
            relationship_type = self._relationship_type(candidate.reason)
            if relationship_type not in self.OPPORTUNITY_RELATIONSHIPS:
                continue

            propagated_impact = source_impact_score * candidate.propagation_weight
            if propagated_impact == 0:
                continue

            direction = (
                OpportunityDirection.INCREASED
                if propagated_impact > 0
                else OpportunityDirection.DECREASED
            )
            changes.append(
                OpportunityChange(
                    source_player_id=source_player_id,
                    source_player_name=source_player_name,
                    affected_player_id=candidate.entity_id,
                    affected_player_name=candidate.entity_name,
                    relationship_type=relationship_type,
                    direction=direction,
                    magnitude=min(1.0, abs(propagated_impact)),
                    reason=candidate.reason,
                )
            )

        return changes

    @staticmethod
    def _relationship_type(reason: str) -> str:
        marker = "--"
        if marker not in reason:
            return ""
        relationship = reason.split(marker, 1)[1].split("(", 1)[0]
        return relationship.strip().casefold()
