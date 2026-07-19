from datetime import datetime, timezone

import pytest

from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.predict.prediction_engine import PredictionEngine


def make_scorecard(
    *,
    overall_score: float = 50.0,
    opportunity_score: float = 50.0,
    health_score: float = 50.0,
    hype_score: float = 50.0,
    risk_score: float = 50.0,
    momentum_score: float = 50.0,
) -> PlayerScorecard:
    return PlayerScorecard(
        player_id="tank-dell",
        player_name="Tank Dell",
        team="HOU",
        overall_score=overall_score,
        opportunity_score=opportunity_score,
        health_score=health_score,
        hype_score=hype_score,
        risk_score=risk_score,
        momentum_score=momentum_score,
        last_updated=datetime.now(timezone.utc),
    )


def test_predicts_rising_trend() -> None:
    engine = PredictionEngine(horizon_days=14)

    scorecard = make_scorecard(
        overall_score=55.0,
        opportunity_score=75.0,
        health_score=70.0,
        hype_score=65.0,
        risk_score=25.0,
        momentum_score=80.0,
    )

    prediction = engine.predict(scorecard)

    assert prediction.entity_id == "tank-dell"
    assert prediction.entity_name == "Tank Dell"
    assert prediction.horizon_days == 14
    assert prediction.projected_trend == "RISING"
    assert prediction.projected_score > prediction.current_score
    assert prediction.score_delta > 0
    assert 0.55 <= prediction.confidence <= 0.90
    assert prediction.reasons


def test_predicts_falling_trend() -> None:
    engine = PredictionEngine()

    scorecard = make_scorecard(
        overall_score=55.0,
        opportunity_score=25.0,
        health_score=30.0,
        hype_score=35.0,
        risk_score=80.0,
        momentum_score=20.0,
    )

    prediction = engine.predict(scorecard)

    assert prediction.projected_trend == "FALLING"
    assert prediction.projected_score < prediction.current_score
    assert prediction.score_delta < 0


def test_predicts_stable_trend() -> None:
    engine = PredictionEngine()

    prediction = engine.predict(make_scorecard())

    assert prediction.projected_trend == "STABLE"
    assert prediction.projected_score == prediction.current_score
    assert prediction.score_delta == 0.0


def test_projected_score_is_bounded() -> None:
    engine = PredictionEngine()

    high_prediction = engine.predict(
        make_scorecard(
            overall_score=99.0,
            opportunity_score=100.0,
            health_score=100.0,
            hype_score=100.0,
            risk_score=0.0,
            momentum_score=100.0,
        )
    )

    low_prediction = engine.predict(
        make_scorecard(
            overall_score=1.0,
            opportunity_score=0.0,
            health_score=0.0,
            hype_score=0.0,
            risk_score=100.0,
            momentum_score=0.0,
        )
    )

    assert high_prediction.projected_score <= 100.0
    assert low_prediction.projected_score >= 0.0


def test_rejects_invalid_horizon() -> None:
    with pytest.raises(ValueError):
        PredictionEngine(horizon_days=0)
