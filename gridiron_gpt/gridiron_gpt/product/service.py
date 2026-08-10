from __future__ import annotations

from dataclasses import asdict

from gridiron_gpt.fantasy_decisions.decision_engine import FantasyDecisionEngine
from gridiron_gpt.fantasy_decisions.models import PlayerDecisionInput, TradeSide
from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository, LeagueProfile


class GridironProductService:
    """Application-facing orchestration shared by API and Streamlit clients."""

    def __init__(
        self,
        league_repository: JsonLeagueProfileRepository,
        decision_engine: FantasyDecisionEngine | None = None,
    ) -> None:
        self.league_repository = league_repository
        self.decision_engine = decision_engine or FantasyDecisionEngine()

    def list_leagues(self) -> list[dict]:
        return [profile.to_dict() for profile in self.league_repository.list()]

    def save_league(self, payload: dict) -> dict:
        profile = LeagueProfile.from_dict(payload)
        self.league_repository.save(profile)
        return profile.to_dict()

    def get_league(self, league_id: str) -> dict:
        return self.league_repository.load(league_id).to_dict()

    def delete_league(self, league_id: str) -> bool:
        return self.league_repository.delete(league_id)

    def draft_rankings(self, league_id: str, players: list[dict]) -> list[dict]:
        league = self.league_repository.load(league_id).to_context()
        decisions = self.decision_engine.rank_draft(self._players(players), league)
        return [asdict(decision) for decision in decisions]

    def start_sit(self, players: list[dict], slots: int) -> list[dict]:
        decisions = self.decision_engine.start_sit(self._players(players), slots=slots)
        return [asdict(decision) for decision in decisions]

    def waivers(self, league_id: str, free_agents: list[dict], roster: list[dict]) -> list[dict]:
        league = self.league_repository.load(league_id).to_context()
        decisions = self.decision_engine.waiver_recommendations(
            self._players(free_agents), league, self._players(roster)
        )
        return [asdict(decision) for decision in decisions]

    def trade(self, give: list[dict], receive: list[dict]) -> dict:
        decision = self.decision_engine.evaluate_trade(
            TradeSide(tuple(self._players(give))),
            TradeSide(tuple(self._players(receive))),
        )
        return asdict(decision)

    def roster_analysis(self, league_id: str, roster: list[dict]) -> dict:
        league = self.league_repository.load(league_id).to_context()
        decision = self.decision_engine.roster_analysis(self._players(roster), league)
        return asdict(decision)

    @staticmethod
    def _players(payloads: list[dict]) -> list[PlayerDecisionInput]:
        return [PlayerDecisionInput(**payload) for payload in payloads]
