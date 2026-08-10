from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.draft_context import CanonicalDraftContext, DraftCapitalTier


class DraftEventFactory:
    def build(self, context: CanonicalDraftContext, *, season: int, team: str | None = None) -> RawEvent:
        tier = context.capital_tier
        rookie = context.is_rookie(season)
        sentiment, impact = self._intelligence(tier, rookie)
        return RawEvent(
            source=context.source,
            headline=(
                f"{context.player_name} draft context: {tier.value} capital"
                + (", rookie season" if rookie else "")
            ),
            player=context.player_name,
            player_id=context.player_id,
            team=team or context.drafted_team,
            event_type="draft_context",
            sentiment=sentiment,
            impact_score=impact,
            confidence=0.9 if tier != DraftCapitalTier.UNKNOWN else 0.5,
            evidence={
                "source_id": f"draft_context:{context.player_id}:{season}",
                "draft_context": {
                    "draft_year": context.draft_year,
                    "draft_round": context.draft_round,
                    "draft_pick": context.draft_pick,
                    "college": context.college,
                    "drafted_team": context.drafted_team,
                    "rookie": rookie,
                    "capital_tier": tier.value,
                    "provenance": context.evidence,
                },
            },
        )

    @staticmethod
    def _intelligence(tier: DraftCapitalTier, rookie: bool) -> tuple[str, float]:
        # Draft capital is a modest prior, never stronger than observed NFL evidence.
        if not rookie:
            return "neutral", 0.0
        if tier == DraftCapitalTier.PREMIUM:
            return "positive", 0.20
        if tier == DraftCapitalTier.EARLY:
            return "positive", 0.10
        return "neutral", 0.0
