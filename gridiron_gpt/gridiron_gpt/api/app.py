from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository
from gridiron_gpt.product.schedule_email import (
    ScheduleEmailRequest,
    ScheduleMailer,
    SmtpScheduleMailer,
)
from gridiron_gpt.product.schedule_generator import (
    GeneratedSchedule,
    ScheduleConfig,
    ScheduleGenerator,
    ScheduleTeam,
)
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


class ScheduleTeamPayload(BaseModel):
    team_id: str
    name: str
    division: str


class SchedulePayload(BaseModel):
    teams: list[ScheduleTeamPayload]
    regular_season_weeks: int
    playoff_start_week: int
    playoff_weeks: int


class ScheduleEmailPayload(BaseModel):
    schedule: SchedulePayload
    recipients: list[str]
    subject: str = "Fantasy Football League Schedule"
    message: str = "The league schedule is attached."
    sender_name: str = "GridironGPT"
    reply_to: str | None = None
    attachment_name: str = "fantasy_schedule.csv"


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


def create_app(
    data_directory: str | Path = "data/leagues",
    schedule_mailer: ScheduleMailer | None = None,
) -> FastAPI:
    service = GridironProductService(JsonLeagueProfileRepository(data_directory))
    app = FastAPI(
        title="GridironGPT API",
        version="1.2.0",
        description=(
            "Product API for league profiles, schedule generation and delivery, "
            "and fantasy decisions."
        ),
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

    @app.post("/schedules/generate")
    def generate_schedule(payload: SchedulePayload) -> dict:
        try:
            schedule, _ = _build_schedule(payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return _schedule_payload(schedule)

    @app.post("/schedules/email")
    def email_schedule(payload: ScheduleEmailPayload) -> dict:
        try:
            schedule, names = _build_schedule(payload.schedule)
            request = ScheduleEmailRequest(
                recipients=tuple(payload.recipients),
                subject=payload.subject,
                message=payload.message,
                sender_name=payload.sender_name,
                reply_to=payload.reply_to,
                attachment_name=payload.attachment_name,
            )
            mailer = schedule_mailer or SmtpScheduleMailer.from_environment()
            result = mailer.send(request, schedule, names)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (RuntimeError, OSError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "sent": result.sent,
            "recipient_count": result.recipient_count,
            "provider": result.provider,
            "detail": result.detail,
        }

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


def _build_schedule(payload: SchedulePayload) -> tuple[GeneratedSchedule, dict[str, str]]:
    teams = tuple(
        ScheduleTeam(team_id=team.team_id, name=team.name, division=team.division)
        for team in payload.teams
    )
    config = ScheduleConfig(
        teams=teams,
        regular_season_weeks=payload.regular_season_weeks,
        playoff_start_week=payload.playoff_start_week,
        playoff_weeks=payload.playoff_weeks,
    )
    return ScheduleGenerator().generate(config), {team.team_id: team.name for team in teams}


def _schedule_payload(schedule: GeneratedSchedule) -> dict:
    return {
        "regular_season_weeks": schedule.config.regular_season_weeks,
        "playoff_weeks": list(schedule.playoff_weeks),
        "home_games": schedule.home_games,
        "away_games": schedule.away_games,
        "matchups": [
            {
                "week": game.week,
                "home_team_id": game.home_team_id,
                "away_team_id": game.away_team_id,
                "divisional": game.divisional,
            }
            for game in schedule.matchups
        ],
    }


app = create_app()
