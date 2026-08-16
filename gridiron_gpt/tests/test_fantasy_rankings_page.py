from types import SimpleNamespace

from apps.streamlit.components.app_shell import (
    NAVIGATION_ITEMS,
    NAVIGATION_SECTIONS,
    build_navigation_markup,
)
from apps.streamlit.pages.fantasy_rankings import (
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
