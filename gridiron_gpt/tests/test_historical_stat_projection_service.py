import pandas as pd
import pytest

from gridiron_gpt.draft.historical_stat_projection_service import HistoricalStatProjectionService


def test_build_blends_per_game_stats_with_recency_weights_and_sample_confidence():
    frames = {
        2023: pd.DataFrame([{"player_display_name": "Player One", "games": 10, "rushing_yards": 500, "rushing_tds": 5}]),
        2024: pd.DataFrame([{"player_display_name": "Player One", "games": 10, "rushing_yards": 600, "rushing_tds": 6}]),
        2025: pd.DataFrame([{"player_display_name": "Player One", "games": 10, "rushing_yards": 700, "rushing_tds": 7}]),
    }
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: frames[season])
    projection = service.build(expected_games=10)["Player One"]
    assert projection.rushing_yards == pytest.approx(640.0 * (10.0 / 17.0))
    assert projection.rushing_touchdowns == pytest.approx(6.4 * (10.0 / 17.0))
    assert projection.games == 10


def test_missing_seasons_renormalize_available_weights_and_damp_small_sample():
    frame = pd.DataFrame([{"player_display_name": "Player One", "games": 10, "receptions": 50}])
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: frame if season == 2025 else pd.DataFrame())
    projection = service.build(expected_games=17)["Player One"]
    assert projection.receptions == pytest.approx(50.0)


def test_full_season_sample_keeps_full_projection_strength():
    frame = pd.DataFrame([{"player_display_name": "Player One", "games": 17, "receptions": 85}])
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: frame if season == 2025 else pd.DataFrame())
    projection = service.build(expected_games=17)["Player One"]
    assert projection.receptions == pytest.approx(85.0)


def test_stat_categories_map_to_projection_model():
    frame = pd.DataFrame([{"player_display_name": "QB One", "games": 17, "passing_yards": 4250, "passing_tds": 34, "interceptions": 10, "rushing_yards": 425, "rushing_tds": 4, "rushing_fumbles_lost": 2, "passing_2pt_conversions": 1}])
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: frame if season == 2025 else pd.DataFrame())
    projection = service.build()["QB One"]
    assert projection.passing_yards == pytest.approx(4250)
    assert projection.passing_touchdowns == pytest.approx(34)
    assert projection.interceptions == pytest.approx(10)
    assert projection.rushing_yards == pytest.approx(425)
    assert projection.rushing_touchdowns == pytest.approx(4)
    assert projection.fumbles_lost == pytest.approx(2)
    assert projection.two_point_conversions == pytest.approx(1)


def test_empty_history_returns_no_projection():
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: pd.DataFrame())
    assert service.build() == {}


def test_negative_expected_games_is_rejected():
    service = HistoricalStatProjectionService(stats_loader=lambda *, season: pd.DataFrame())
    with pytest.raises(ValueError, match="expected_games cannot be negative"):
        service.build(expected_games=-1)
