from datetime import datetime, timezone

from gridiron_cortex.facade.cortex_facade import CortexFacade
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.jsonl_game_state_repository import JsonlGameStateRepository
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository


def test_facade_explanation_includes_real_football_context(tmp_path):
    football_state_dir = tmp_path / "football_state"
    cortex_dir = tmp_path / "cortex"

    player_repo = JsonlPlayerStateRepository(
        football_state_dir / "player_states.jsonl"
    )
    game_repo = JsonlGameStateRepository(
        football_state_dir / "game_states.jsonl"
    )

    player_repo.save(
        CanonicalPlayerState(
            player_id="00-0039163",
            player_name="C.J. Stroud",
            team="HOU",
            position="QB",
            roster_status="ACT",
            status_description_abbr="A01",
            roster_week=1,
            roster_game_type="REG",
        )
    )

    kickoff = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)

    for week in list(range(1, 8)) + list(range(9, 19)):
        if week == 1:
            game_repo.save(
                CanonicalGameState(
                    game_id="2026_01_BUF_HOU",
                    season=2026,
                    week=1,
                    season_type="REG",
                    home_team="HOU",
                    away_team="BUF",
                    kickoff_at=kickoff,
                    game_status="scheduled",
                )
            )
        else:
            game_repo.save(
                CanonicalGameState(
                    game_id=f"2026_{week:02d}_HOU_OPP",
                    season=2026,
                    week=week,
                    season_type="REG",
                    home_team="HOU",
                    away_team="OPP",
                    kickoff_at=datetime(2026, 9, min(week + 1, 28), 17, 0, tzinfo=timezone.utc),
                    game_status="scheduled",
                )
            )

    catalog = [{
        "player": "C.J. Stroud",
        "gsis_id": "00-0039163",
        "team": "HOU",
        "position": "QB",
        "aliases": ["C.J. Stroud", "CJ Stroud"],
    }]

    facade = CortexFacade(
        data_directory=cortex_dir,
        catalog_loader=lambda: catalog,
        football_state_directory=football_state_dir,
        football_season=2026,
    )

    result = facade.process_event(
        RawEvent(
            headline="C.J. Stroud continues preparing for the 2026 season",
            source="test",
            player="C.J. Stroud",
            team="HOU",
            event_type="news",
            sentiment="neutral",
            impact_score=0.0,
            confidence=1.0,
            evidence={
                "source_id": "facade-football-context-test",
                "reasons": ["Facade football-context integration test."],
            },
        )
    )

    player_entity = next(
        entity for entity in result.entities
        if entity.entity_type == "player"
    )

    assert player_entity.player_id == "00-0039163"
    assert "Football context: C.J. Stroud is available." in result.explanation
    assert "Next game: Week 1 vs BUF home." in result.explanation
    assert "Bye week: 8." in result.explanation
