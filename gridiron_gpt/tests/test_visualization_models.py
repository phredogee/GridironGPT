from gridiron_gpt.intelligence.visualization_models import (
    build_cortex_timeline,
    build_signal_breakdown,
    confidence_components,
    position_rankings,
    recommendation_distribution,
    team_momentum,
)


def signals():
    return [
        {
            "date": "2026-08-01",
            "headline": "Returned to practice",
            "impact": "positive",
            "value": 1.0,
            "source": "NBC",
        },
        {
            "date": "2026-08-03",
            "headline": "Expected larger workload",
            "impact": "positive",
            "value": 0.5,
            "source": "PFT",
        },
    ]


def test_signal_breakdown_orders_by_absolute_impact():
    rows = build_signal_breakdown(signals())
    assert rows[0].label == "Returned to practice"
    assert rows[0].value == 1.0


def test_cortex_timeline_calculates_running_score():
    rows = build_cortex_timeline(signals())
    assert rows[0].cumulative_score == 1.0
    assert rows[1].cumulative_score == 1.5


def test_confidence_components_reports_signal_agreement():
    result = confidence_components(signals())
    assert result == {
        "agreement": 1.0,
        "positive_share": 1.0,
        "negative_share": 0.0,
    }


def test_platform_chart_models_group_scores():
    scores = {
        ("Player A", "DET"): {"score": 2.0},
        ("Player B", "DET"): {"score": -0.5},
        ("Player C", "HOU"): {"score": 0.5},
    }
    positions = {"Player A": "RB", "Player B": "WR", "Player C": "WR"}

    distribution = {row.label: row.value for row in recommendation_distribution(scores)}
    assert distribution["BUY"] == 1
    assert distribution["WATCH"] == 1
    assert distribution["MONITOR"] == 1

    teams = {row.label: row.value for row in team_momentum(scores)}
    assert teams["DET"] == 1.5
    assert teams["HOU"] == 0.5

    rankings = position_rankings(scores, positions)
    assert rankings["RB"][0].label == "Player A"
    assert rankings["WR"][0].label == "Player C"
