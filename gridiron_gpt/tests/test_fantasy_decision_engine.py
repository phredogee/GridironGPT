import pytest

from gridiron_gpt.fantasy_decisions.decision_engine import FantasyDecisionEngine
from gridiron_gpt.fantasy_decisions.models import (
    LeagueContext,
    PlayerDecisionInput,
    RecommendationAction,
    ScoringFormat,
    TradeSide,
)


def player(name, position="RB", **overrides):
    values = {
        "player_id": name.lower().replace(" ", "-"),
        "player_name": name,
        "position": position,
        "team": "ATL",
        "cortex_score": 10.0,
        "confidence": 0.8,
        "projected_points": 12.0,
        "replacement_value": 2.0,
    }
    values.update(overrides)
    return PlayerDecisionInput(**values)


def test_decision_score_combines_cortex_projection_and_context():
    engine = FantasyDecisionEngine()
    base = player("Base")
    boosted = player("Boosted", matchup_factor=0.2, trend_factor=0.2)
    assert engine.decision_score(boosted) > engine.decision_score(base)


def test_availability_reduces_decision_score():
    engine = FantasyDecisionEngine()
    healthy = player("Healthy")
    risky = player("Risky", availability_factor=0.5)
    assert engine.decision_score(risky) < engine.decision_score(healthy)


def test_bye_week_has_zero_start_value():
    assert FantasyDecisionEngine().decision_score(player("Bye", bye_week=True)) == 0


def test_draft_rankings_are_sorted_and_explainable():
    decisions = FantasyDecisionEngine().rank_draft(
        [player("Low", projected_points=8), player("High", projected_points=18)],
        LeagueContext(roster_size=1),
    )
    assert decisions[0].player_name == "High"
    assert decisions[0].metadata["rank"] == 1
    assert decisions[0].reasons


def test_start_sit_selects_top_available_players():
    decisions = FantasyDecisionEngine().start_sit(
        [player("One", projected_points=18), player("Two", projected_points=12)],
        slots=1,
    )
    assert decisions[0].action == RecommendationAction.START
    assert decisions[1].action == RecommendationAction.SIT


def test_start_sit_does_not_start_bye_player():
    decisions = FantasyDecisionEngine().start_sit(
        [player("Bye", projected_points=30, bye_week=True), player("Active", projected_points=10)],
        slots=1,
    )
    active = next(decision for decision in decisions if decision.player_name == "Active")
    bye = next(decision for decision in decisions if decision.player_name == "Bye")
    assert active.action == RecommendationAction.START
    assert bye.action == RecommendationAction.SIT


def test_start_slots_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        FantasyDecisionEngine().start_sit([player("One")], slots=0)


def test_waiver_engine_prioritizes_roster_need():
    league = LeagueContext(starting_slots={"QB": 1, "RB": 2, "WR": 2, "TE": 1})
    roster = [player("QB One", "QB"), player("RB One"), player("WR One", "WR")]
    free_agents = [
        player("TE Target", "TE", projected_points=9),
        player("RB Target", "RB", projected_points=9),
    ]
    decisions = FantasyDecisionEngine().waiver_recommendations(free_agents, league, roster)
    assert decisions[0].player_name == "TE Target"
    assert "Roster need at TE" in decisions[0].reasons


def test_waiver_add_includes_faab_bid():
    decisions = FantasyDecisionEngine().waiver_recommendations(
        [player("Breakout", projected_points=20, trend_factor=0.3)],
        LeagueContext(faab_budget=100),
        [],
    )
    assert decisions[0].action == RecommendationAction.ADD
    assert 1 <= decisions[0].metadata["faab_bid"] <= 100


def test_low_value_waiver_is_pass():
    candidate = player(
        "Low",
        cortex_score=0,
        projected_points=0,
        replacement_value=0,
        confidence=0.5,
    )
    decision = FantasyDecisionEngine().waiver_recommendations(
        [candidate], LeagueContext(), [player("QB", "QB"), player("RB1"), player("RB2"), player("RB3"), player("WR1", "WR"), player("WR2", "WR"), player("WR3", "WR"), player("TE", "TE")]
    )[0]
    assert decision.action == RecommendationAction.PASS


def test_trade_accepts_positive_value_delta():
    decision = FantasyDecisionEngine().evaluate_trade(
        TradeSide((player("Give", projected_points=8),)),
        TradeSide((player("Receive", projected_points=18),)),
    )
    assert decision.action == RecommendationAction.ACCEPT
    assert decision.score > 0


def test_trade_rejects_negative_value_delta():
    decision = FantasyDecisionEngine().evaluate_trade(
        TradeSide((player("Give", projected_points=20),)),
        TradeSide((player("Receive", projected_points=5),)),
    )
    assert decision.action == RecommendationAction.REJECT


def test_near_even_trade_is_hold():
    decision = FantasyDecisionEngine().evaluate_trade(
        TradeSide((player("Give", projected_points=12),)),
        TradeSide((player("Receive", projected_points=12.5),)),
    )
    assert decision.action == RecommendationAction.HOLD


def test_roster_analysis_identifies_missing_positions():
    decision = FantasyDecisionEngine().roster_analysis(
        [player("QB", "QB"), player("RB", "RB")],
        LeagueContext(),
    )
    assert decision.action == RecommendationAction.TARGET
    assert "WR" in decision.metadata["weak_positions"]
    assert "TE" in decision.metadata["weak_positions"]


def test_balanced_roster_can_hold():
    roster = [
        player("QB", "QB"),
        player("RB1"), player("RB2"), player("RB3"),
        player("WR1", "WR"), player("WR2", "WR"), player("WR3", "WR"),
        player("TE", "TE"),
    ]
    decision = FantasyDecisionEngine().roster_analysis(roster, LeagueContext())
    assert decision.action == RecommendationAction.HOLD


def test_player_input_validates_confidence():
    with pytest.raises(ValueError, match="confidence"):
        player("Bad", confidence=1.2)


def test_league_context_validates_teams():
    with pytest.raises(ValueError, match="teams"):
        LeagueContext(teams=1)


def test_scoring_format_is_explicit():
    league = LeagueContext(scoring_format=ScoringFormat.PPR)
    assert league.scoring_format == ScoringFormat.PPR
