from gridiron_cortex.decide.recommendation_engine import (
    RecommendationEngine,
)
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.score_update import ScoreUpdate


def make_update(
    score_delta: float,
    entity_name: str = "Tank Dell",
) -> ScoreUpdate:
    return ScoreUpdate(
        entity_type="player",
        entity_name=entity_name,
        team="HOU",
        score_delta=score_delta,
        reason="Recent event changed the player score",
    )


def make_prediction(
    trend: str,
    *,
    entity_name: str = "Tank Dell",
    confidence: float = 0.80,
    score_delta: float = 4.0,
) -> Prediction:
    return Prediction(
        entity_id="tank-dell",
        entity_name=entity_name,
        horizon_days=14,
        projected_trend=trend,
        current_score=55.0,
        projected_score=55.0 + score_delta,
        score_delta=score_delta,
        confidence=confidence,
        reasons=["Forecast evidence"],
    )


def test_generate_remains_backward_compatible() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(1.0)]
    )[0]

    assert recommendation.action == "BUY"
    assert recommendation.confidence == 75.0


def test_rising_prediction_strengthens_positive_signal() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(1.0)],
        predictions=[make_prediction("RISING")],
    )[0]

    assert recommendation.action == "BUY"
    assert recommendation.confidence > 75.0
    assert "14-day forecast: rising" in recommendation.reasons


def test_falling_prediction_weakens_positive_signal() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(1.0)],
        predictions=[
            make_prediction(
                "FALLING",
                score_delta=-4.0,
            )
        ],
    )[0]

    assert recommendation.action == "BUY"
    assert recommendation.confidence < 75.0


def test_rising_prediction_moves_hold_to_watch() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(0.0)],
        predictions=[make_prediction("RISING")],
    )[0]

    assert recommendation.action == "WATCH"
    assert recommendation.confidence > 50.0


def test_falling_prediction_moves_hold_to_monitor() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(0.0)],
        predictions=[
            make_prediction(
                "FALLING",
                score_delta=-4.0,
            )
        ],
    )[0]

    assert recommendation.action == "MONITOR"
    assert recommendation.confidence > 50.0


def test_prediction_matching_is_case_insensitive() -> None:
    engine = RecommendationEngine()

    recommendation = engine.generate(
        [make_update(1.0, entity_name="Tank Dell")],
        predictions=[
            make_prediction(
                "RISING",
                entity_name="tank dell",
            )
        ],
    )[0]

    assert recommendation.confidence > 75.0
