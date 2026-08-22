from types import SimpleNamespace

from apps.streamlit.components.app_shell import (
    NAVIGATION_ITEMS,
    NAVIGATION_SECTIONS,
    build_navigation_markup,
)
from apps.streamlit.pages.fantasy_rankings import (
    _best_available_scores,
    _best_value_scores,
    _remaining_population,
    build_fantasy_ranking_snapshot,
    render_fantasy_rankings,
)
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation


def test_rankings_is_exposed_under_fantasy_navigation():
    assert "Rankings" in NAVIGATION_ITEMS

    fantasy = next(
        section for section in NAVIGATION_SECTIONS
        if section["label"] == "Fantasy"
    )

    assert "Rankings" in fantasy["pages"]
    assert "?page=Rankings" in build_navigation_markup("Rankings")


def test_rankings_page_exposes_snapshot_builder_and_renderer():
    assert callable(build_fantasy_ranking_snapshot)
    assert callable(render_fantasy_rankings)


def test_draft_mode_removes_player_from_overall_position_and_explained_views():
    drafted = SimpleNamespace(player_id="p1", player_name="Drafted RB", position="RB")
    available = SimpleNamespace(player_id="p2", player_name="Available RB", position="RB")
    receiver = SimpleNamespace(player_id="p3", player_name="Available WR", position="WR")

    population = FantasyRankingPopulation(
        overall=[drafted, available, receiver],
        by_position={
            "QB": [],
            "RB": [drafted, available],
            "WR": [receiver],
            "TE": [],
        },
        explained_overall=[
            SimpleNamespace(score=drafted),
            SimpleNamespace(score=available),
            SimpleNamespace(score=receiver),
        ],
    )

    remaining = _remaining_population(population, {"p1"})

    assert [row.player_id for row in remaining.overall] == ["p2", "p3"]
    assert [row.player_id for row in remaining.by_position["RB"]] == ["p2"]
    assert [row.score.player_id for row in remaining.explained_overall] == ["p2", "p3"]


def test_draft_mode_empty_selection_preserves_population_object():
    population = FantasyRankingPopulation(
        overall=[],
        by_position={"QB": [], "RB": [], "WR": [], "TE": []},
        explained_overall=[],
    )

    assert _remaining_population(population, set()) is population


def test_best_available_skips_drafted_players_without_reordering_board():
    scores = [
        SimpleNamespace(player_id="p1"),
        SimpleNamespace(player_id="p2"),
        SimpleNamespace(player_id="p3"),
        SimpleNamespace(player_id="p4"),
    ]
    population = FantasyRankingPopulation(
        overall=scores,
        by_position={},
        explained_overall=[],
    )

    result = _best_available_scores(population, {"p1", "p3"}, limit=2)

    assert [score.player_id for score in result] == ["p2", "p4"]


def test_best_value_uses_positive_draft_value_and_skips_drafted_players():
    scores = [
        SimpleNamespace(player_id="p1"),
        SimpleNamespace(player_id="p2"),
        SimpleNamespace(player_id="p3"),
        SimpleNamespace(player_id="p4"),
    ]
    population = FantasyRankingPopulation(
        overall=scores,
        by_position={},
        explained_overall=[],
    )
    market_views = {
        "p1": SimpleNamespace(draft_value=15.0, overall_rank=1),
        "p2": SimpleNamespace(draft_value=4.0, overall_rank=2),
        "p3": SimpleNamespace(draft_value=-2.0, overall_rank=3),
        "p4": SimpleNamespace(draft_value=9.0, overall_rank=4),
    }

    result = _best_value_scores(population, market_views, {"p1"}, limit=3)

    assert [score.player_id for score in result] == ["p4", "p2"]
