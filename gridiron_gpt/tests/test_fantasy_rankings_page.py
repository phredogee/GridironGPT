from apps.streamlit.components.app_shell import (
    NAVIGATION_ITEMS,
    NAVIGATION_SECTIONS,
    build_navigation_markup,
)
from apps.streamlit.pages.fantasy_rankings import (
    build_fantasy_ranking_snapshot,
    render_fantasy_rankings,
)


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
