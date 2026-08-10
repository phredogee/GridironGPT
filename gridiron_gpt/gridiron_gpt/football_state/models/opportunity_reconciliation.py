from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from gridiron_gpt.football_state.models.opportunity_change import OpportunityChange
from gridiron_gpt.football_state.models.usage_trend import UsageTrendResult


class OpportunityConfirmation(str, Enum):
    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class OpportunityReconciliationResult:
    player_id: str
    player_name: str
    confirmation: OpportunityConfirmation
    predicted: OpportunityChange
    observed: UsageTrendResult
    confidence: float
    reason: str
