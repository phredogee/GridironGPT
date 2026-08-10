from gridiron_gpt.intelligence.nflverse_signal_factory import (
    compare_weekly_records,
    generate_weekly_signals,
)
from gridiron_gpt.intelligence.nflverse_signal_factory import (
    compare_weekly_records,
    generate_rolling_baseline_signals,
    generate_weekly_signals,
)


def test_target_increase_creates_opportunity_signal():
    previous = {
        "player_id": "P001",
        "player_name": "Test Receiver",
        "team": "DAL",
        "position": "WR",
        "season": 2025,
        "week": 1,
        "statistics": {
            "targets": 4,
        },
    }

    current = {
        "player_id": "P001",
        "player_name": "Test Receiver",
        "team": "DAL",
        "position": "WR",
        "season": 2025,
        "week": 2,
        "statistics": {
            "targets": 10,
        },
    }

    signals = compare_weekly_records(previous, current)

    assert len(signals) == 1
    assert signals[0]["signal_type"] == "opportunity"
    assert signals[0]["metric"] == "targets"
    assert signals[0]["delta"] == 6
    assert signals[0]["sentiment"] == "positive"
    assert signals[0]["impact_score"] > 0


def test_small_change_does_not_create_signal():
    previous = {
        "player_id": "P001",
        "player_name": "Test Receiver",
        "season": 2025,
        "week": 1,
        "statistics": {
            "targets": 5,
        },
    }

    current = {
        "player_id": "P001",
        "player_name": "Test Receiver",
        "season": 2025,
        "week": 2,
        "statistics": {
            "targets": 7,
        },
    }

    signals = compare_weekly_records(previous, current)

    assert signals == []


def test_usage_drop_creates_negative_signal():
    previous = {
        "player_id": "P002",
        "player_name": "Test Running Back",
        "season": 2025,
        "week": 4,
        "statistics": {
            "carries": 18,
        },
    }

    current = {
        "player_id": "P002",
        "player_name": "Test Running Back",
        "season": 2025,
        "week": 5,
        "statistics": {
            "carries": 8,
        },
    }

    signals = compare_weekly_records(previous, current)

    assert len(signals) == 1
    assert signals[0]["metric"] == "carries"
    assert signals[0]["delta"] == -10
    assert signals[0]["sentiment"] == "negative"
    assert signals[0]["impact_score"] < 0


def test_generates_signals_for_adjacent_player_weeks():
    records = [
        {
            "player_id": "P001",
            "player_name": "Player One",
            "season": 2025,
            "week": 2,
            "statistics": {
                "targets": 10,
            },
        },
        {
            "player_id": "P001",
            "player_name": "Player One",
            "season": 2025,
            "week": 1,
            "statistics": {
                "targets": 4,
            },
        },
        {
            "player_id": "P002",
            "player_name": "Player Two",
            "season": 2025,
            "week": 1,
            "statistics": {
                "carries": 10,
            },
        },
        {
            "player_id": "P002",
            "player_name": "Player Two",
            "season": 2025,
            "week": 2,
            "statistics": {
                "carries": 11,
            },
        },
    ]

    signals = generate_weekly_signals(records)

    assert len(signals) == 1
    assert signals[0]["player_name"] == "Player One"


def test_does_not_compare_across_seasons():
    records = [
        {
            "player_id": "P001",
            "player_name": "Player One",
            "season": 2024,
            "week": 18,
            "statistics": {
                "targets": 2,
            },
        },
        {
            "player_id": "P001",
            "player_name": "Player One",
            "season": 2025,
            "week": 1,
            "statistics": {
                "targets": 12,
            },
        },
    ]

    signals = generate_weekly_signals(records)

    assert signals == []

def test_rolling_baseline_generates_opportunity_signal():
    records = [
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 1,
            "statistics": {"targets": 4},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 2,
            "statistics": {"targets": 5},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 3,
            "statistics": {"targets": 6},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 4,
            "statistics": {"targets": 11},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert len(signals) == 1

    signal = signals[0]

    assert signal["metric"] == "targets"
    assert signal["signal_type"] == "opportunity"
    assert signal["signal_method"] == "rolling_baseline"
    assert signal["baseline_value"] == 5.0
    assert signal["current_value"] == 11
    assert signal["delta"] == 6.0
    assert signal["confidence"] == 0.94


def test_rolling_baseline_ignores_small_change():
    records = [
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 1,
            "statistics": {"targets": 5},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 2,
            "statistics": {"targets": 6},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 3,
            "statistics": {"targets": 5},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 4,
            "statistics": {"targets": 7},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert signals == []


def test_rolling_baseline_requires_enough_history():
    records = [
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 1,
            "statistics": {"targets": 2},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 2,
            "statistics": {"targets": 12},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert signals == []


def test_rolling_baseline_does_not_cross_seasons():
    records = [
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2024,
            "week": 17,
            "statistics": {"targets": 3},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2024,
            "week": 18,
            "statistics": {"targets": 4},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 1,
            "statistics": {"targets": 5},
        },
        {
            "player_id": "P001",
            "player_name": "Test Receiver",
            "season": 2025,
            "week": 2,
            "statistics": {"targets": 12},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    assert signals == []


def test_rolling_production_signal_has_lower_confidence():
    records = [
        {
            "player_id": "P002",
            "player_name": "Test Quarterback",
            "season": 2025,
            "week": 1,
            "statistics": {"passing_yards": 200},
        },
        {
            "player_id": "P002",
            "player_name": "Test Quarterback",
            "season": 2025,
            "week": 2,
            "statistics": {"passing_yards": 210},
        },
        {
            "player_id": "P002",
            "player_name": "Test Quarterback",
            "season": 2025,
            "week": 3,
            "statistics": {"passing_yards": 190},
        },
        {
            "player_id": "P002",
            "player_name": "Test Quarterback",
            "season": 2025,
            "week": 4,
            "statistics": {"passing_yards": 350},
        },
    ]

    signals = generate_rolling_baseline_signals(records)

    passing_signal = next(
        signal
        for signal in signals
        if signal["metric"] == "passing_yards"
    )

    assert passing_signal["baseline_value"] == 200.0
    assert passing_signal["delta"] == 150.0
    assert passing_signal["confidence"] == 0.78
