from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.matchup_context import MatchupContext, MatchupTendency
from gridiron_gpt.football_state.models.schedule_context import UpcomingScheduleContext


class ScheduleEventFactory:
    """Convert schedule and matchup context into structured Cortex evidence."""

    SOURCE = "canonical schedule context"

    def build_schedule_event(
        self,
        context: UpcomingScheduleContext,
        *,
        player_id: str,
        player_name: str,
    ) -> RawEvent:
        sentiment, impact = self._schedule_intelligence(context)
        next_game = context.next_game
        headline = (
            f"{player_name} schedule context: bye week"
            if context.bye_week
            else f"{player_name} next opponent: {context.opponent or 'unknown'}"
        )

        return RawEvent(
            source=self.SOURCE,
            headline=headline,
            player=player_name,
            player_id=player_id,
            team=context.team,
            event_type="schedule_context",
            sentiment=sentiment,
            impact_score=impact,
            confidence=0.9 if next_game is not None or context.bye_week else 0.5,
            evidence={
                "source_id": self._schedule_source_id(context, player_id),
                "schedule_context": {
                    "season": context.season,
                    "as_of_week": context.as_of_week,
                    "next_game_id": next_game.game_id if next_game else None,
                    "opponent": context.opponent,
                    "venue_side": context.venue_side.value if context.venue_side else None,
                    "bye_week": context.bye_week,
                    "days_rest": context.days_rest,
                    "short_rest": context.short_rest,
                    "extended_rest": context.extended_rest,
                },
            },
        )

    def build_matchup_event(
        self,
        context: MatchupContext,
        *,
        player_id: str,
        player_name: str,
    ) -> RawEvent:
        sentiment, impact = self._matchup_intelligence(context)
        return RawEvent(
            source=context.source,
            headline=(
                f"{player_name} {context.position} matchup vs {context.opponent} "
                f"is {context.tendency.value}: {context.reason}"
            ),
            player=player_name,
            player_id=player_id,
            team=context.team,
            event_type="matchup_context",
            sentiment=sentiment,
            impact_score=impact,
            confidence=context.confidence,
            evidence={
                "source_id": self._matchup_source_id(context, player_id),
                "matchup_context": {
                    "opponent": context.opponent,
                    "position": context.position,
                    "season": context.season,
                    "week": context.week,
                    "tendency": context.tendency.value,
                    "score": context.score,
                    "reason": context.reason,
                    "metrics": [
                        {
                            "name": metric.name,
                            "value": metric.value,
                            "league_average": metric.league_average,
                            "favorable_delta": metric.favorable_delta,
                            "sample_games": metric.sample_games,
                        }
                        for metric in context.metrics
                    ],
                    "provenance": context.evidence,
                },
            },
        )

    @staticmethod
    def _schedule_intelligence(context: UpcomingScheduleContext) -> tuple[str, float]:
        # Schedule facts are contextual modifiers, not standalone fantasy takes.
        if context.bye_week:
            return "neutral", 0.0
        if context.short_rest:
            return "negative", -0.15
        if context.extended_rest:
            return "positive", 0.10
        return "neutral", 0.0

    @staticmethod
    def _matchup_intelligence(context: MatchupContext) -> tuple[str, float]:
        if context.tendency == MatchupTendency.FAVORABLE:
            return "positive", min(0.45, max(0.1, abs(context.score)))
        if context.tendency == MatchupTendency.UNFAVORABLE:
            return "negative", -min(0.45, max(0.1, abs(context.score)))
        return "neutral", 0.0

    @staticmethod
    def _schedule_source_id(context: UpcomingScheduleContext, player_id: str) -> str:
        game_id = context.next_game.game_id if context.next_game else "none"
        return ":".join([
            "schedule_context",
            player_id,
            str(context.season),
            str(context.as_of_week),
            game_id,
        ])

    @staticmethod
    def _matchup_source_id(context: MatchupContext, player_id: str) -> str:
        return ":".join([
            "matchup_context",
            player_id,
            str(context.season),
            str(context.week),
            context.opponent,
            context.position,
        ])
