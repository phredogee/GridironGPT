from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from gridiron_gpt.fantasy_decisions.decision_engine import FantasyDecisionEngine
from gridiron_gpt.fantasy_decisions.models import LeagueContext, PlayerDecisionInput


@dataclass(frozen=True)
class DraftPick:
    overall_pick: int
    round_number: int
    pick_in_round: int
    fantasy_team_id: str
    player_id: str
    player_name: str
    position: str
    selected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DraftRoomState:
    league: LeagueContext
    team_ids: tuple[str, ...]
    rounds: int
    picks: list[DraftPick] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.team_ids) != self.league.teams:
            raise ValueError("team_ids must match league team count")
        if self.rounds <= 0:
            raise ValueError("rounds must be positive")
        if len(set(self.team_ids)) != len(self.team_ids):
            raise ValueError("team_ids must be unique")

    @property
    def next_overall_pick(self) -> int:
        return len(self.picks) + 1

    def team_on_clock(self) -> str | None:
        if self.next_overall_pick > self.rounds * len(self.team_ids):
            return None
        round_number = (self.next_overall_pick - 1) // len(self.team_ids) + 1
        index = (self.next_overall_pick - 1) % len(self.team_ids)
        order = self.team_ids if round_number % 2 else tuple(reversed(self.team_ids))
        return order[index]

    def draft_player(self, team_id: str, player: PlayerDecisionInput) -> DraftPick:
        expected = self.team_on_clock()
        if expected is None:
            raise ValueError("draft is complete")
        if team_id != expected:
            raise ValueError(f"{expected} is on the clock")
        if any(pick.player_id == player.player_id for pick in self.picks):
            raise ValueError("player has already been drafted")
        overall = self.next_overall_pick
        round_number = (overall - 1) // len(self.team_ids) + 1
        pick_in_round = (overall - 1) % len(self.team_ids) + 1
        pick = DraftPick(
            overall_pick=overall,
            round_number=round_number,
            pick_in_round=pick_in_round,
            fantasy_team_id=team_id,
            player_id=player.player_id,
            player_name=player.player_name,
            position=player.position,
        )
        self.picks.append(pick)
        return pick

    def roster_for(self, team_id: str) -> list[DraftPick]:
        return [pick for pick in self.picks if pick.fantasy_team_id == team_id]


class DraftRoomService:
    def __init__(self, engine: FantasyDecisionEngine | None = None):
        self.engine = engine or FantasyDecisionEngine()

    def recommend(
        self,
        state: DraftRoomState,
        available_players: list[PlayerDecisionInput],
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        team_id = state.team_on_clock()
        if team_id is None:
            return []
        drafted_ids = {pick.player_id for pick in state.picks}
        available = [player for player in available_players if player.player_id not in drafted_ids]
        decisions = self.engine.rank_draft(available, state.league)
        roster_positions = [pick.position for pick in state.roster_for(team_id)]
        results = []
        for decision in decisions[:limit]:
            need_bonus = 1.0 if decision.metadata.get("position") not in roster_positions else 0.0
            results.append(
                {
                    "player_id": decision.player_id,
                    "player_name": decision.player_name,
                    "score": round(decision.score + need_bonus, 4),
                    "confidence": decision.confidence,
                    "reasons": list(decision.reasons),
                    "team_on_clock": team_id,
                }
            )
        results.sort(key=lambda row: row["score"], reverse=True)
        return results
