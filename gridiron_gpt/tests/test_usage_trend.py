import pytest

from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState
from gridiron_gpt.football_state.models.usage_trend import UsageTrendDirection
from gridiron_gpt.football_state.services.usage_trend_service import UsageTrendService


def state(week, **overrides):
    values = {
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "season": 2026,
        "week": week,
        "team": "ATL",
        "position": "RB",
        "snap_share": 0.60,
        "route_participation": 0.55,
        "carries": 12,
        "targets": 5,
        "carry_share": 0.55,
        "target_share": 0.35,
        "red_zone_opportunities": 3,
    }
    values.update(overrides)
    return CanonicalUsageState(**values)


def test_rising_usage_is_detected_against_recent_baseline():
    current = state(4, snap_share=0.76, carries=18, targets=8, carry_share=0.82, target_share=0.57)
    history = [state(1), state(2), state(3)]

    result = UsageTrendService().analyze(current, history)

    assert result.direction == UsageTrendDirection.RISING
    assert result.prior_games == 3
    assert result.deltas["carries"].baseline == 12
    assert result.deltas["carries"].delta == 6


def test_falling_usage_is_detected():
    current = state(4, snap_share=0.42, carries=7, targets=2, carry_share=0.30, target_share=0.15)

    result = UsageTrendService().analyze(current, [state(1), state(2), state(3)])

    assert result.direction == UsageTrendDirection.FALLING


def test_small_changes_are_stable():
    current = state(4, snap_share=0.62, carries=13, targets=6, carry_share=0.57, target_share=0.37)

    result = UsageTrendService().analyze(current, [state(1), state(2), state(3)])

    assert result.direction == UsageTrendDirection.STABLE


def test_conflicting_usage_changes_are_mixed():
    current = state(4, snap_share=0.75, carries=18, targets=2, target_share=0.15)

    result = UsageTrendService().analyze(current, [state(1), state(2), state(3)])

    assert result.direction == UsageTrendDirection.MIXED


def test_no_prior_games_returns_unknown():
    result = UsageTrendService().analyze(state(1), [])

    assert result.direction == UsageTrendDirection.UNKNOWN
    assert result.prior_games == 0


def test_partial_metrics_use_only_available_comparisons():
    current = state(3, snap_share=None, route_participation=None, carries=18, targets=None, carry_share=0.80, target_share=None)
    history = [
        state(1, snap_share=None, route_participation=None, targets=None, target_share=None),
        state(2, snap_share=None, route_participation=None, targets=None, target_share=None),
    ]

    result = UsageTrendService().analyze(current, history)

    assert result.direction == UsageTrendDirection.RISING
    assert "snap_share" not in result.deltas
    assert "carries" in result.deltas


def test_only_recent_baseline_window_is_used():
    history = [
        state(1, carries=30),
        state(2, carries=10),
        state(3, carries=10),
        state(4, carries=10),
    ]

    result = UsageTrendService().analyze(state(5, carries=13), history, baseline_games=3)

    assert result.prior_games == 3
    assert result.deltas["carries"].baseline == 10
    assert result.deltas["carries"].delta == 3


def test_other_players_do_not_contaminate_baseline():
    other = state(3, player_id="allgeier", player_name="Tyler Allgeier", carries=30)

    result = UsageTrendService().analyze(state(4, carries=15), [state(2), other])

    assert result.prior_games == 1
    assert result.deltas["carries"].baseline == 12


def test_baseline_window_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        UsageTrendService().analyze(state(4), [state(3)], baseline_games=0)
