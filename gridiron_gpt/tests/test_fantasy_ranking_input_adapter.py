from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_gpt.draft.fantasy_ranking_input_adapter import (
    FantasyRankingInputAdapter,
    FantasyRankingSourceValues,
)
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


def _player(**overrides):
    values = {
        "player_id": "00-0039163",
        "player_name": "C.J. Stroud",
        "team": "HOU",
        "position": "QB",
        "roster_status": "ACT",
        "status_description_abbr": "A01",
    }
    values.update(overrides)
    return CanonicalPlayerState(**values)


def test_builds_normalized_inputs_from_real_source_shapes():
    adapter = FantasyRankingInputAdapter()
    scorecard = PlayerScorecard(
        player_id="00-0039163",
        player_name="C.J. Stroud",
        team="HOU",
        position="QB",
        overall_score=62.0,
    )

    result = adapter.build(
        _player(),
        source_values=FantasyRankingSourceValues(
            historical_points=300.0,
            historical_max_points=400.0,
            adp=25.0,
            draft_pool_size=180,
            role_score=90.0,
            role_provenance="projected starting QB",
        ),
        cortex_scorecard=scorecard,
    )

    assert result.baseline_score == 75.0
    assert round(result.market_score, 3) == round(((180 - 25 + 1) / 180) * 100, 3)
    assert result.role_score == 90.0
    assert result.cortex_score == 62.0
    assert result.availability_score == 100.0
    assert result.provenance["role"] == "projected starting QB"


def test_missing_sources_remain_missing_instead_of_becoming_zero():
    result = FantasyRankingInputAdapter().build(_player())

    assert result.baseline_score is None
    assert result.market_score is None
    assert result.role_score is None
    assert result.cortex_score is None
    assert result.availability_score == 100.0
    assert "baseline" not in result.provenance
    assert "market" not in result.provenance


def test_unknown_availability_remains_missing():
    result = FantasyRankingInputAdapter().build(
        _player(roster_status=None)
    )

    assert result.availability_score is None
    assert "availability" not in result.provenance


def test_reserve_status_receives_explicit_availability_penalty():
    result = FantasyRankingInputAdapter().build(
        _player(roster_status="RES")
    )

    assert result.availability_score == 35.0
    assert result.provenance["availability"] == "canonical football state: reserve"


def test_adp_outside_draft_pool_clamps_to_zero():
    result = FantasyRankingInputAdapter().build(
        _player(),
        source_values=FantasyRankingSourceValues(
            adp=250.0,
            draft_pool_size=180,
        ),
    )

    assert result.market_score == 0.0


def test_invalid_historical_denominator_is_treated_as_missing():
    result = FantasyRankingInputAdapter().build(
        _player(),
        source_values=FantasyRankingSourceValues(
            historical_points=100.0,
            historical_max_points=0.0,
        ),
    )

    assert result.baseline_score is None
