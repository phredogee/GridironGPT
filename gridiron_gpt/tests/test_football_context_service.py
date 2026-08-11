from datetime import datetime, timezone

from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.jsonl_game_state_repository import JsonlGameStateRepository
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository
from gridiron_gpt.football_state.services.football_context_service import FootballContextService
from gridiron_gpt.football_state.services.player_availability_classifier import PlayerAvailability
from gridiron_gpt.football_state.services.schedule_state_service import ScheduleStateService


NOW = datetime(2026, 8, 11, tzinfo=timezone.utc)


def _service(tmp_path):
    players = JsonlPlayerStateRepository(tmp_path / "players.jsonl")
    games = JsonlGameStateRepository(tmp_path / "games.jsonl")
    schedule = ScheduleStateService(games, season=2026, schedule_loader=lambda: [], clock=lambda: NOW)
    return players, games, FootballContextService(players, schedule)


def test_context_combines_player_availability_and_next_game(tmp_path):
    players, games, service = _service(tmp_path)
    players.save(CanonicalPlayerState(
        player_id="00-1234567",
        player_name="Test Player",
        team="HOU",
        position="WR",
        roster_status="ACT",
    ))
    games.save(CanonicalGameState(
        game_id="2026_01_BUF_HOU",
        season=2026,
        week=1,
        season_type="REG",
        home_team="HOU",
        away_team="BUF",
        kickoff_at=datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc),
        game_status="scheduled",
    ))

    context = service.for_player("00-1234567", as_of=NOW)

    assert context is not None
    assert context.availability is PlayerAvailability.AVAILABLE
    assert context.next_game is not None
    assert context.next_game.game_id == "2026_01_BUF_HOU"
    assert context.opponent == "BUF"
    assert context.location == "HOME"
    assert context.bye_week == 2


def test_context_detects_real_bye_between_games(tmp_path):
    players, games, service = _service(tmp_path)
    players.save(CanonicalPlayerState(player_id="00-1234567", player_name="Test Player", team="HOU", roster_status="RES"))
    for week in list(range(1, 8)) + list(range(9, 19)):
        games.save(CanonicalGameState(
            game_id=f"2026_{week:02d}_HOU_OPP",
            season=2026,
            week=week,
            season_type="REG",
            home_team="HOU",
            away_team="OPP",
            kickoff_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
            game_status="scheduled",
        ))

    context = service.for_player("00-1234567", as_of=NOW)

    assert context is not None
    assert context.availability is PlayerAvailability.RESERVE
    assert context.bye_week == 8


def test_context_returns_none_for_unknown_player(tmp_path):
    _players, _games, service = _service(tmp_path)

    assert service.for_player("missing") is None


def test_context_without_team_has_no_schedule_context(tmp_path):
    players, _games, service = _service(tmp_path)
    players.save(CanonicalPlayerState(player_id="00-1234567", player_name="Free Agent", roster_status="CUT"))

    context = service.for_player("00-1234567", as_of=NOW)

    assert context is not None
    assert context.availability is PlayerAvailability.RELEASED
    assert context.next_game is None
    assert context.opponent is None
    assert context.location is None
    assert context.bye_week is None
