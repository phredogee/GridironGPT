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
        "provenance": {
            "baseline": "historical fantasy production",
            "market": "ADP",
            "role": "roster/depth context",
            "cortex": "Cortex overall score",
            "availability": "football state",
        },
    }
    values.update(overrides)
    return FantasyRankingInputs(**values)


def test_default_weights_sum_to_one():
    FantasyRankingWeights().validate()


def test_invalid_weights_are_rejected():
    with pytest.raises(ValueError, match="sum to 1.0"):
        FantasyRankingWeights(baseline=0.50).validate()


def test_negative_weight_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        FantasyRankingWeights(
            baseline=0.65,
            market=0.20,
            role=0.10,
            cortex=0.10,
            availability=-0.05,
        ).validate()


def test_score_uses_explicit_weighted_components():
    result = FantasyRankingScorer().score(_inputs())

    # 80*.55 + 70*.20 + 90*.10 + 60*.10 + 100*.05 = 78
    assert result.ranking_score == 78.0
    assert result.weighted_components == {
        "baseline": 44.0,
        "market": 14.0,
        "role": 9.0,
        "cortex": 6.0,
        "availability": 5.0,
    }


def test_score_clamps_inputs_to_zero_to_one_hundred():
    result = FantasyRankingScorer().score(
        _inputs(
            baseline_score=120,
            market_score=-10,
            role_score=150,
            cortex_score=-1,
            availability_score=200,
        )
    )

    assert result.components == {
        "baseline": 100.0,
        "market": 0.0,
        "role": 100.0,
        "cortex": 0.0,
        "availability": 100.0,
    }
    assert result.ranking_score == 70.0


def test_provenance_is_preserved_for_explanations():
    result = FantasyRankingScorer().score(_inputs())

    assert result.provenance["market"] == "ADP"
    assert result.provenance["cortex"] == "Cortex overall score"


def test_custom_weights_can_disable_cortex_adjustment():
    scorer = FantasyRankingScorer(
        FantasyRankingWeights(
            baseline=0.60,
            market=0.20,
            role=0.10,
            cortex=0.00,
            availability=0.10,
        )
    )

    low_cortex = scorer.score(_inputs(cortex_score=0))
    high_cortex = scorer.score(_inputs(cortex_score=100))

    assert low_cortex.ranking_score == high_cortex.ranking_score


def test_missing_component_renormalizes_remaining_weights():
    result = FantasyRankingScorer().score(
        _inputs(
            market_score=None,
        )
    )

    # Active configured weight is .80. The missing market component contributes
    # neither zero points nor a penalty; remaining weights are normalized to 1.
    expected = (
        80 * (0.55 / 0.80)
        + 90 * (0.10 / 0.80)
        + 60 * (0.10 / 0.80)
        + 100 * (0.05 / 0.80)
    )
    assert result.ranking_score == round(expected, 3)
    assert "market" not in result.components
    assert "market" not in result.weighted_components
    assert "market" not in result.provenance


def test_zero_is_real_evidence_not_missing_evidence():
    zero_market = FantasyRankingScorer().score(_inputs(market_score=0.0))
    missing_market = FantasyRankingScorer().score(_inputs(market_score=None))

    assert "market" in zero_market.components
    assert zero_market.components["market"] == 0.0
    assert zero_market.ranking_score < missing_market.ranking_score


def test_all_weighted_components_missing_is_rejected():
    with pytest.raises(
        ValueError,
        match="at least one weighted ranking component must be available",
    ):
        FantasyRankingScorer().score(
            _inputs(
                baseline_score=None,
                market_score=None,
                role_score=None,
                cortex_score=None,
                availability_score=None,
            )
        )
