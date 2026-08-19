import pytest

from gridiron_gpt.draft.fantasy_ranking_score import (
    FantasyRankingInputs,
    FantasyRankingScorer,
    FantasyRankingWeights,
)


def _inputs(**overrides):
    values = {
        "player_id": "00-0039163",
        "player_name": "C.J. Stroud",
        "team": "HOU",
        "position": "QB",
        "baseline_score": 80.0,
        "market_score": 70.0,
        "role_score": 90.0,
        "cortex_score": 60.0,
        "availability_score": 100.0,
        "projection_score": 50.0,
        "provenance": {
            "baseline": "historical fantasy production",
            "market": "ADP",
            "role": "roster/depth context",
            "cortex": "Cortex overall score",
            "availability": "football state",
            "projection": "position-normalized projection",
        },
    }
    values.update(overrides)
    return FantasyRankingInputs(**values)


def test_default_weights_sum_to_one_and_reserve_five_percent_for_projection():
    weights = FantasyRankingWeights()
    weights.validate()
    assert weights.projection == 0.05
    assert weights.baseline == pytest.approx(0.55 * 0.95)
    assert weights.market == pytest.approx(0.20 * 0.95)
    assert weights.role == pytest.approx(0.10 * 0.95)
    assert weights.cortex == pytest.approx(0.10 * 0.95)
    assert weights.availability == pytest.approx(0.05 * 0.95)


def test_invalid_weights_are_rejected():
    with pytest.raises(ValueError, match="sum to 1.0"):
        FantasyRankingWeights(baseline=0.50).validate()


def test_negative_weight_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        FantasyRankingWeights(
            baseline=0.55,
            market=0.20,
            role=0.10,
            cortex=0.10,
            availability=0.05,
            projection=-0.05,
        ).validate()


def test_score_uses_five_percent_projection_and_scaled_existing_components():
    result = FantasyRankingScorer().score(_inputs())

    expected = 80*.5225 + 70*.19 + 90*.095 + 60*.095 + 100*.0475 + 50*.05
    assert result.ranking_score == round(expected, 3)
    assert result.weighted_components == {
        "baseline": 41.8,
        "market": 13.3,
        "role": 8.55,
        "cortex": 5.7,
        "availability": 4.75,
        "projection": 2.5,
    }


def test_score_clamps_inputs_to_zero_to_one_hundred():
    result = FantasyRankingScorer().score(
        _inputs(
            baseline_score=120,
            market_score=-10,
            role_score=150,
            cortex_score=-1,
            availability_score=200,
            projection_score=150,
        )
    )

    assert result.components == {
        "baseline": 100.0,
        "market": 0.0,
        "role": 100.0,
        "cortex": 0.0,
        "availability": 100.0,
        "projection": 100.0,
    }
    assert result.ranking_score == 71.5


def test_provenance_is_preserved_for_explanations():
    result = FantasyRankingScorer().score(_inputs())

    assert result.provenance["market"] == "ADP"
    assert result.provenance["cortex"] == "Cortex overall score"
    assert result.provenance["projection"] == "position-normalized projection"


def test_custom_weights_can_disable_cortex_adjustment():
    scorer = FantasyRankingScorer(
        FantasyRankingWeights(
            baseline=0.55,
            market=0.20,
            role=0.10,
            cortex=0.00,
            availability=0.10,
            projection=0.05,
        )
    )

    low_cortex = scorer.score(_inputs(cortex_score=0))
    high_cortex = scorer.score(_inputs(cortex_score=100))

    assert low_cortex.ranking_score == high_cortex.ranking_score


def test_missing_component_renormalizes_remaining_weights():
    result = FantasyRankingScorer().score(_inputs(market_score=None))
    active = 1.0 - 0.19
    expected = (
        80 * (0.5225 / active)
        + 90 * (0.095 / active)
        + 60 * (0.095 / active)
        + 100 * (0.0475 / active)
        + 50 * (0.05 / active)
    )
    assert result.ranking_score == round(expected, 3)
    assert "market" not in result.components
    assert "market" not in result.weighted_components
    assert "market" not in result.provenance


def test_missing_projection_is_neutral_and_renormalizes_existing_model():
    result = FantasyRankingScorer().score(_inputs(projection_score=None))
    expected = 80*.55 + 70*.20 + 90*.10 + 60*.10 + 100*.05
    assert result.ranking_score == round(expected, 3)
    assert "projection" not in result.components
    assert "projection" not in result.weighted_components
    assert "projection" not in result.provenance


def test_zero_is_real_evidence_not_missing_evidence():
    zero_market = FantasyRankingScorer().score(_inputs(market_score=0.0))
    missing_market = FantasyRankingScorer().score(_inputs(market_score=None))

    assert "market" in zero_market.components
    assert zero_market.components["market"] == 0.0
    assert zero_market.ranking_score < missing_market.ranking_score


def test_availability_only_is_rejected_as_insufficient_ranking_evidence():
    with pytest.raises(ValueError, match="at least one anchor ranking evidence component must be available"):
        FantasyRankingScorer().score(
            _inputs(
                baseline_score=None,
                market_score=None,
                role_score=None,
                cortex_score=None,
                availability_score=100.0,
                projection_score=None,
            )
        )


def test_role_and_availability_without_anchor_evidence_are_rejected():
    with pytest.raises(ValueError, match="at least one anchor ranking evidence component must be available"):
        FantasyRankingScorer().score(
            _inputs(
                baseline_score=None,
                market_score=None,
                role_score=70.0,
                cortex_score=None,
                availability_score=100.0,
                projection_score=None,
            )
        )


def test_market_can_anchor_ranking_without_historical_baseline():
    result = FantasyRankingScorer().score(
        _inputs(
            baseline_score=None,
            market_score=90.0,
            role_score=None,
            cortex_score=50.0,
            availability_score=100.0,
            projection_score=None,
        )
    )
    assert result.components == {"market": 90.0, "cortex": 50.0, "availability": 100.0}


def test_baseline_can_anchor_ranking_without_market():
    result = FantasyRankingScorer().score(
        _inputs(
            baseline_score=75.0,
            market_score=None,
            role_score=80.0,
            cortex_score=None,
            availability_score=100.0,
            projection_score=None,
        )
    )
    assert result.components == {"baseline": 75.0, "role": 80.0, "availability": 100.0}


def test_all_weighted_components_missing_is_rejected():
    with pytest.raises(ValueError, match="at least one weighted ranking component must be available"):
        FantasyRankingScorer().score(
            _inputs(
                baseline_score=None,
                market_score=None,
                role_score=None,
                cortex_score=None,
                availability_score=None,
                projection_score=None,
            )
        )
