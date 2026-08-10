from gridiron_gpt.intelligence.signal_aggregator import (
    aggregate_signals,
)


def make_signal(
    *,
    week,
    method,
    direction,
    impact,
    confidence=0.90,
    metric="targets",
):
    return {
        "source": "nflverse",
        "player_id": "P001",
        "player_name": "Test Receiver",
        "team": "DAL",
        "position": "WR",
        "season": 2025,
        "current_week": week,
        "metric": metric,
        "signal_type": "opportunity",
        "signal_method": method,
        "direction": direction,
        "sentiment": (
            "positive"
            if direction in {"increased", "above"}
            else "negative"
        ),
        "impact_score": impact,
        "confidence": confidence,
        "reason": f"Test signal for Week {week}.",
    }


def test_single_signal_is_emerging():
    result = aggregate_signals(
        weekly_signals=[
            make_signal(
                week=4,
                method="weekly_delta",
                direction="increased",
                impact=0.60,
            )
        ],
        rolling_signals=[],
    )

    assert len(result) == 1
    assert (
        result[0]["trend_classification"]
        == "emerging"
    )
    assert result[0]["evidence_count"] == 1


def test_weekly_and_rolling_agreement_is_confirmed():
    weekly = make_signal(
        week=4,
        method="weekly_delta",
        direction="increased",
        impact=0.60,
    )

    rolling = make_signal(
        week=4,
        method="rolling_baseline",
        direction="above",
        impact=0.55,
    )

    result = aggregate_signals(
        weekly_signals=[weekly],
        rolling_signals=[rolling],
    )

    assert (
        result[0]["trend_classification"]
        == "confirmed"
    )
    assert result[0]["evidence_count"] == 2
    assert result[0]["confidence"] > 0.90


def test_three_matching_weeks_are_sustained():
    weekly_signals = [
        make_signal(
            week=4,
            method="weekly_delta",
            direction="increased",
            impact=0.40,
        ),
        make_signal(
            week=5,
            method="weekly_delta",
            direction="increased",
            impact=0.50,
        ),
        make_signal(
            week=6,
            method="weekly_delta",
            direction="increased",
            impact=0.60,
        ),
    ]

    result = aggregate_signals(
        weekly_signals=weekly_signals,
        rolling_signals=[],
    )

    assert (
        result[0]["trend_classification"]
        == "sustained"
    )
    assert result[0]["weeks"] == [4, 5, 6]


def test_mixed_recent_directions_are_volatile():
    weekly_signals = [
        make_signal(
            week=4,
            method="weekly_delta",
            direction="increased",
            impact=0.70,
        ),
        make_signal(
            week=5,
            method="weekly_delta",
            direction="decreased",
            impact=-0.80,
        ),
    ]

    result = aggregate_signals(
        weekly_signals=weekly_signals,
        rolling_signals=[],
    )

    assert (
        result[0]["trend_classification"]
        == "volatile"
    )
    assert abs(result[0]["impact_score"]) < 0.20


def test_groups_different_metrics_separately():
    weekly_signals = [
        make_signal(
            week=4,
            method="weekly_delta",
            direction="increased",
            impact=0.60,
            metric="targets",
        ),
        make_signal(
            week=4,
            method="weekly_delta",
            direction="increased",
            impact=0.40,
            metric="receiving_yards",
        ),
    ]

    result = aggregate_signals(
        weekly_signals=weekly_signals,
        rolling_signals=[],
    )

    assert len(result) == 2

    metrics = {
        aggregate["metric"]
        for aggregate in result
    }

    assert metrics == {
        "targets",
        "receiving_yards",
    }


def test_different_players_are_grouped_separately():
    first = make_signal(
        week=4,
        method="weekly_delta",
        direction="increased",
        impact=0.60,
    )

    second = {
        **make_signal(
            week=4,
            method="weekly_delta",
            direction="increased",
            impact=0.50,
        ),
        "player_id": "P002",
        "player_name": "Second Receiver",
    }

    result = aggregate_signals(
        weekly_signals=[first, second],
        rolling_signals=[],
    )

    assert len(result) == 2
