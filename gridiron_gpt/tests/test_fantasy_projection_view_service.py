from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_projection_view_service import (
    build_projection_views,
    projection_view_for_player,
)


def test_projection_views_expose_points_and_ppg_by_case_insensitive_name():
    projections = {
        "Ja'Marr Chase": SimpleNamespace(
            fantasy=SimpleNamespace(projected_points=331.78, projected_ppg=19.52)
        )
    }

    views = build_projection_views(projections)
    view = projection_view_for_player("JA'MARR CHASE", views)

    assert view is not None
    assert view.projected_points == 331.78
    assert view.projected_ppg == 19.52


def test_projection_view_returns_none_when_player_has_no_history():
    assert projection_view_for_player("Rookie Player", {}) is None
