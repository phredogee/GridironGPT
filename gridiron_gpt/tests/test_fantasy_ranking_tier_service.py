from gridiron_gpt.draft.consensus_adp_service import ConsensusAdpService
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore
from gridiron_gpt.draft.fantasy_ranking_tier_service import FantasyRankingTierService


def score(player_id, name, position, ranking_score):
    return FantasyRankingScore(
        player_id=player_id,
        player_name=name,
        team="TST",
        position=position,
        ranking_score=ranking_score,
        components={"baseline": ranking_score},
        weighted_components={"baseline": ranking_score},
        provenance={"baseline": "test"},
    )


def test_assigns_position_rank_and_tiers_from_score_gaps():
    scores = [
        score("rb1", "RB One", "RB", 90.0),
        score("wr1", "WR One", "WR", 89.0),
        score("rb2", "RB Two", "RB", 88.5),
        score("rb3", "RB Three", "RB", 82.0),
        score("rb4", "RB Four", "RB", 81.0),
    ]

    views = FantasyRankingTierService(minimum_tier_gap=2.5).build(scores)

    assert views["rb1"].position_rank == 1
    assert views["rb2"].position_rank == 2
    assert views["rb3"].position_rank == 3
    assert views["rb1"].tier == 1
    assert views["rb2"].tier == 1
    assert views["rb3"].tier == 2
    assert views["rb4"].tier == 2
    assert views["wr1"].position_rank == 1
    assert views["wr1"].tier == 1


def test_calculates_consensus_rank_value_without_affecting_score():
    scores = [
        score("p1", "Player One", "WR", 90.0),
        score("p2", "Player Two", "WR", 80.0),
    ]
    consensus = ConsensusAdpService().build(
        {
            "ESPN": {"Player One": 5.0, "Player Two": 20.0},
            "NFL": {"Player One": 7.0, "Player Two": 22.0},
        }
    )

    views = FantasyRankingTierService().build(
        scores,
        consensus_adp_by_key=consensus,
    )

    assert views["p1"].overall_rank == 1
    assert views["p1"].consensus_adp == 6.0
    assert views["p1"].draft_value == 5.0
    assert views["p1"].adp_source_count == 2
    assert views["p1"].adp_spread == 2.0
    assert views["p2"].overall_rank == 2
    assert views["p2"].consensus_adp == 21.0
    assert views["p2"].draft_value == 19.0


def test_single_source_adp_has_no_spread():
    scores = [score("p1", "Player One", "RB", 88.0)]
    consensus = ConsensusAdpService().build(
        {"ESPN": {"Player One": 4.5}}
    )

    view = FantasyRankingTierService().build(
        scores,
        consensus_adp_by_key=consensus,
    )["p1"]

    assert view.consensus_adp == 4.5
    assert view.adp_source_count == 1
    assert view.adp_spread is None
    assert view.source_adps == {"ESPN": 4.5}


def test_missing_consensus_adp_remains_missing_market_metadata():
    scores = [score("p1", "Player One", "QB", 75.0)]

    view = FantasyRankingTierService().build(scores)["p1"]

    assert view.consensus_adp is None
    assert view.adp_source_count == 0
    assert view.adp_spread is None
    assert view.draft_value is None


def test_tier_service_requires_positive_minimum_gap():
    try:
        FantasyRankingTierService(minimum_tier_gap=0)
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
