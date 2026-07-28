from types import SimpleNamespace

from gridiron_cortex.decide.recommendation_engine import (
    RecommendationEngine,
)
from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)
from gridiron_cortex.models.intelligence_context import (
    IntelligenceContext,
)


def build_score_update(
    score_delta: float,
):
    return SimpleNamespace(
        entity_type="player",
        entity_name="Tank Dell",
        team="HOU",
        score_delta=score_delta,
        reason="Test score update",
    )


def build_intelligence(
    *,
    has_conflict: bool,
    confidence_penalty: float = 0.0,
) -> IntelligenceContext:
    return IntelligenceContext(
        contradiction=ContradictionResult(
            has_conflict=has_conflict,
            severity=0.5 if has_conflict else 0.0,
            confidence_penalty=confidence_penalty,
            conflicting_sources=(
                ["Source A", "Source B"]
                if has_conflict
                else []
            ),
            explanation=(
                "Sources report conflicting information."
                if has_conflict
                else ""
            ),
        )
    )


def test_no_contradiction_preserves_buy():
    engine = RecommendationEngine()
    update = build_score_update(score_delta=1.0)
    intelligence = build_intelligence(
        has_conflict=False,
    )

    recommendations = engine.generate(
        [update],
        intelligence=intelligence,
    )

    recommendation = recommendations[0]

    assert recommendation.action == "BUY"
    assert recommendation.confidence == 75.0


def test_contradiction_changes_buy_to_watch():
    engine = RecommendationEngine()
    update = build_score_update(score_delta=1.0)
    intelligence = build_intelligence(
        has_conflict=True,
        confidence_penalty=0.10,
    )

    recommendations = engine.generate(
        [update],
        intelligence=intelligence,
    )

    recommendation = recommendations[0]

    assert recommendation.action == "WATCH"


def test_contradiction_changes_sell_to_monitor():
    engine = RecommendationEngine()
    update = build_score_update(score_delta=-1.0)
    intelligence = build_intelligence(
        has_conflict=True,
        confidence_penalty=0.10,
    )

    recommendations = engine.generate(
        [update],
        intelligence=intelligence,
    )

    recommendation = recommendations[0]

    assert recommendation.action == "MONITOR"


def test_contradiction_reduces_confidence():
    engine = RecommendationEngine()
    update = build_score_update(score_delta=1.0)
    intelligence = build_intelligence(
        has_conflict=True,
        confidence_penalty=0.20,
    )

    recommendations = engine.generate(
        [update],
        intelligence=intelligence,
    )

    recommendation = recommendations[0]

    assert recommendation.confidence == 55.0
