import pytest

from gridiron_gpt.draft.fantasy_projection_service import (
    FantasyProjectionService,
    FantasyScoring,
    PlayerStatProjection,
)


def test_ppr_projection_scores_standard_offensive_stats():
    service = FantasyProjectionService()
    stats = PlayerStatProjection(
        games=17,
        rushing_yards=1000,
        rushing_touchdowns=10,
        receptions=60,
        receiving_yards=500,
        receiving_touchdowns=3,
        fumbles_lost=2,
    )

    projection = service.project(stats, scoring=FantasyScoring.PPR)

    assert projection.projected_points == 284.0
    assert projection.projected_ppg == 16.71


def test_scoring_format_only_changes_reception_component():
    service = FantasyProjectionService()
    stats = PlayerStatProjection(games=10, receptions=40, receiving_yards=600)

    standard = service.project(stats, scoring="standard")
    half_ppr = service.project(stats, scoring="half_ppr")
    ppr = service.project(stats, scoring="ppr")

    assert standard.projected_points == 60.0
    assert half_ppr.projected_points == 80.0
    assert ppr.projected_points == 100.0


def test_quarterback_projection_uses_passing_and_rushing_scoring():
    service = FantasyProjectionService()
    stats = PlayerStatProjection(
        games=17,
        passing_yards=4000,
        passing_touchdowns=30,
        interceptions=10,
        rushing_yards=500,
        rushing_touchdowns=5,
    )

    projection = service.project(stats)

    assert projection.projected_points == 340.0
    assert projection.projected_ppg == 20.0


def test_zero_games_has_no_ppg_instead_of_dividing_by_zero():
    projection = FantasyProjectionService().project(
        PlayerStatProjection(games=0, rushing_yards=100)
    )

    assert projection.projected_points == 10.0
    assert projection.projected_ppg is None


def test_negative_yardage_is_allowed_and_scores_normally():
    projection = FantasyProjectionService().project(
        PlayerStatProjection(games=1, receiving_yards=-5)
    )

    assert projection.projected_points == -0.5
    assert projection.projected_ppg == -0.5


def test_negative_nonnegative_counting_stats_are_rejected():
    with pytest.raises(ValueError, match="receptions cannot be negative"):
        FantasyProjectionService().project(PlayerStatProjection(receptions=-1))
