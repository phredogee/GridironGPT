from __future__ import annotations

from collections import Counter

from gridiron_gpt.fantasy_decisions.models import (
    DecisionType,
    FantasyDecision,
    LeagueContext,
    PlayerDecisionInput,
    RecommendationAction,
    TradeSide,
)


class FantasyDecisionEngine:
    """Translate calibrated Cortex context into explainable fantasy actions."""

    def decision_score(self, player: PlayerDecisionInput) -> float:
        if player.bye_week:
            return 0.0
        base = (
            0.45 * player.cortex_score
            + 0.35 * player.projected_points
            + 0.20 * player.replacement_value
        )
        contextual = 4.0 * player.matchup_factor + 4.0 * player.trend_factor
        return round((base + contextual) * player.availability_factor, 4)

    def rank_draft(
        self,
        players: list[PlayerDecisionInput],
        league: LeagueContext,
    ) -> list[FantasyDecision]:
        ranked = sorted(players, key=self.decision_score, reverse=True)
        decisions = []
        for rank, player in enumerate(ranked, start=1):
            score = self.decision_score(player)
            reasons = self._player_reasons(player)
            decisions.append(
                FantasyDecision(
                    decision_type=DecisionType.DRAFT,
                    action=RecommendationAction.DRAFT if rank <= league.roster_size else RecommendationAction.TARGET,
                    player_id=player.player_id,
                    player_name=player.player_name,
                    score=score,
                    confidence=player.confidence,
                    summary=f"Draft rank {rank}: {player.player_name}",
                    reasons=reasons,
                    metadata={"rank": rank, "position": player.position},
                )
            )
        return decisions

    def start_sit(
        self,
        candidates: list[PlayerDecisionInput],
        *,
        slots: int = 1,
    ) -> list[FantasyDecision]:
        if slots <= 0:
            raise ValueError("slots must be positive")
        ranked = sorted(candidates, key=self.decision_score, reverse=True)
        decisions = []
        for index, player in enumerate(ranked):
            start = index < slots and not player.bye_week and player.availability_factor > 0
            alternatives = tuple(p.player_name for p in ranked if p.player_id != player.player_id)[:3]
            decisions.append(
                FantasyDecision(
                    decision_type=DecisionType.START_SIT,
                    action=RecommendationAction.START if start else RecommendationAction.SIT,
                    player_id=player.player_id,
                    player_name=player.player_name,
                    score=self.decision_score(player),
                    confidence=player.confidence,
                    summary=f"{'Start' if start else 'Sit'} {player.player_name}",
                    reasons=self._player_reasons(player),
                    alternatives=alternatives,
                    metadata={"position": player.position, "slot_count": slots},
                )
            )
        return decisions

    def waiver_recommendations(
        self,
        free_agents: list[PlayerDecisionInput],
        league: LeagueContext,
        roster: list[PlayerDecisionInput],
    ) -> list[FantasyDecision]:
        needs = self._position_needs(roster, league)
        ranked = sorted(
            free_agents,
            key=lambda player: self.decision_score(player) + needs.get(player.position, 0.0),
            reverse=True,
        )
        decisions = []
        for player in ranked:
            score = self.decision_score(player) + needs.get(player.position, 0.0)
            action = RecommendationAction.ADD if score > 5.0 else RecommendationAction.PASS
            faab = 0
            if action == RecommendationAction.ADD and league.faab_budget:
                faab = max(1, min(league.faab_budget, round(score * player.confidence)))
            reasons = list(self._player_reasons(player))
            if needs.get(player.position, 0.0) > 0:
                reasons.append(f"Roster need at {player.position}")
            decisions.append(
                FantasyDecision(
                    decision_type=DecisionType.WAIVER,
                    action=action,
                    player_id=player.player_id,
                    player_name=player.player_name,
                    score=round(score, 4),
                    confidence=player.confidence,
                    summary=f"{'Add' if action == RecommendationAction.ADD else 'Pass on'} {player.player_name}",
                    reasons=tuple(reasons),
                    metadata={"faab_bid": faab, "position": player.position},
                )
            )
        return decisions

    def evaluate_trade(
        self,
        give: TradeSide,
        receive: TradeSide,
        *,
        threshold: float = 2.0,
    ) -> FantasyDecision:
        delta = receive.value - give.value
        if delta > threshold:
            action = RecommendationAction.ACCEPT
        elif delta < -threshold:
            action = RecommendationAction.REJECT
        else:
            action = RecommendationAction.HOLD
        received_names = ", ".join(player.player_name for player in receive.players)
        given_names = ", ".join(player.player_name for player in give.players)
        return FantasyDecision(
            decision_type=DecisionType.TRADE,
            action=action,
            player_id=None,
            player_name=None,
            score=round(delta, 4),
            confidence=self._trade_confidence(give, receive),
            summary=f"{action.value.title()} trade: give {given_names}; receive {received_names}",
            reasons=(
                f"Receive-side value: {receive.value:.2f}",
                f"Give-side value: {give.value:.2f}",
                f"Net value: {delta:+.2f}",
            ),
            metadata={"give": given_names, "receive": received_names},
        )

    def roster_analysis(
        self,
        roster: list[PlayerDecisionInput],
        league: LeagueContext,
    ) -> FantasyDecision:
        counts = Counter(player.position for player in roster)
        needs = self._position_needs(roster, league)
        unavailable = [
            player.player_name
            for player in roster
            if player.availability_factor < 0.5 or player.bye_week
        ]
        weak_positions = tuple(position for position, need in needs.items() if need > 0)
        score = -sum(needs.values()) - len(unavailable)
        reasons = [f"Roster counts: {dict(counts)}"]
        if weak_positions:
            reasons.append(f"Needs depth at: {', '.join(weak_positions)}")
        if unavailable:
            reasons.append(f"Unavailable/bye: {', '.join(unavailable)}")
        if not weak_positions and not unavailable:
            reasons.append("No immediate roster weakness detected")
        return FantasyDecision(
            decision_type=DecisionType.ROSTER,
            action=RecommendationAction.TARGET if weak_positions else RecommendationAction.HOLD,
            player_id=None,
            player_name=None,
            score=float(score),
            confidence=0.9,
            summary="Roster needs analysis",
            reasons=tuple(reasons),
            metadata={"weak_positions": weak_positions, "unavailable": tuple(unavailable)},
        )

    @staticmethod
    def _player_reasons(player: PlayerDecisionInput) -> tuple[str, ...]:
        reasons = [
            f"Cortex score {player.cortex_score:.2f}",
            f"Projected points {player.projected_points:.2f}",
            f"Confidence {player.confidence:.0%}",
        ]
        if player.trend_factor > 0:
            reasons.append("Usage/football trend is improving")
        elif player.trend_factor < 0:
            reasons.append("Usage/football trend is declining")
        if player.matchup_factor > 0:
            reasons.append("Favorable matchup context")
        elif player.matchup_factor < 0:
            reasons.append("Unfavorable matchup context")
        if player.bye_week:
            reasons.append("Player is on bye")
        if player.availability_factor < 1.0:
            reasons.append("Availability risk reduces expected value")
        return tuple(reasons)

    @staticmethod
    def _position_needs(
        roster: list[PlayerDecisionInput],
        league: LeagueContext,
    ) -> dict[str, float]:
        counts = Counter(player.position for player in roster)
        needs: dict[str, float] = {}
        for position in ("QB", "RB", "WR", "TE"):
            required = league.starting_slots.get(position, 0)
            buffer = 1 if position in {"RB", "WR"} else 0
            missing = max(0, required + buffer - counts.get(position, 0))
            needs[position] = float(missing * 3)
        return needs

    @staticmethod
    def _trade_confidence(give: TradeSide, receive: TradeSide) -> float:
        players = give.players + receive.players
        if not players:
            return 0.0
        return round(sum(player.confidence for player in players) / len(players), 4)
