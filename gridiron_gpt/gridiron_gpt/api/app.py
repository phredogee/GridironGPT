from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository
from gridiron_gpt.product.service import GridironProductService


class LeaguePayload(BaseModel):
    league_id: str
    name: str
    teams: int = 12
    roster_size: int = 16
    starting_slots: dict[str, int] = Field(
        default_factory=lambda: {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}
    )
    bench_slots: int = 6
    ir_slots: int = 1
    faab_budget: int = 100
    scoring_format: str = "half_ppr"


class PlayersPayload(BaseModel):
    players: list[dict[str, Any]]


class StartSitPayload(PlayersPayload):
    slots: int = 1


class WaiverPayload(BaseModel):
    league_id: str
    free_agents: list[dict[str, Any]]
    roster: list[dict[str, Any]]


class TradePayload(BaseModel):
    give: list[dict[str, Any]]
    receive: list[dict[str, Any]]


class RosterPayload(BaseModel):
    league_id: str
    roster: list[dict[str, Any]]


def create_app(data_directory: str | Path = "data/leagues") -> FastAPI:
    service = GridironProductService(JsonLeagueProfileRepository(data_directory))
    app = FastAPI(
        title="GridironGPT API",
        version="1.0.0",
        description="Product API for league profiles and fantasy decisions.",
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": "gridiron-gpt"}

    @app.get("/leagues")
    def list_leagues() -> list[dict]:
        return service.list_leagues()

    @app.post("/leagues")
    def save_league(payload: LeaguePayload) -> dict:
        try:
            return service.save_league(payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/leagues/{league_id}")
    def get_league(league_id: str) -> dict:
        try:
            return service.get_league(league_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.delete("/leagues/{league_id}")
    def delete_league(league_id: str) -> dict:
        return {"deleted": service.delete_league(league_id)}

    @app.post("/decisions/draft/{league_id}")
    def draft(league_id: str, payload: PlayersPayload) -> list[dict]:
        return _league_call(lambda: service.draft_rankings(league_id, payload.players))

    @app.post("/decisions/start-sit")
    def start_sit(payload: StartSitPayload) -> list[dict]:
        try:
            return service.start_sit(payload.players, payload.slots)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/decisions/waivers")
    def waivers(payload: WaiverPayload) -> list[dict]:
        return _league_call(
            lambda: service.waivers(payload.league_id, payload.free_agents, payload.roster)
        )

    @app.post("/decisions/trade")
    def trade(payload: TradePayload) -> dict:
        return service.trade(payload.give, payload.receive)

    @app.post("/decisions/roster")
    def roster(payload: RosterPayload) -> dict:
        return _league_call(lambda: service.roster_analysis(payload.league_id, payload.roster))

    def _league_call(callback):
        try:
            return callback()
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()
