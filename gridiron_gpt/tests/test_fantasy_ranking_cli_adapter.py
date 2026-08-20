from gridiron_gpt.draft.fantasy_ranking_cli_adapter import production_rankings_to_cli_frame
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore


def _score(name: str, position: str, team: str, ranking_score: float, baseline: float):
    return FantasyRankingScore(
        player_id=name.lower().replace(" ", "-"),
        player_name=name,
        team=team,
        position=position,
        ranking_score=ranking_score,
        components={"baseline": baseline, "projection": 80.0},
        weighted_components={"baseline": baseline * 0.95, "projection": 4.0},
        provenance={},
    )


def test_adapter_preserves_production_order_and_score():
    first = _score("Player One", "RB", "BUF", 91.25, 88.0)
    second = _score("Player Two", "WR", "DET", 87.5, 82.0)
    population = FantasyRankingPopulation(
        overall=[first, second],
        by_position={"RB": [first], "WR": [second]},
        explained_overall=[],
    )

    frame = production_rankings_to_cli_frame(
        population,
        adp_by_name={"Player One": 7.5, "Player Two": 14.0},
        teams=12,
    )

    assert frame["name"].tolist() == ["Player One", "Player Two"]
    assert frame["rank"].tolist() == [1, 2]
    assert frame["composite"].tolist() == [91.25, 87.5]
    assert frame["adp"].tolist() == [7.5, 14.0]
    assert frame["position"].tolist() == ["RB", "WR"]
    assert frame["team"].tolist() == ["BUF", "DET"]
    assert frame["hist_score"].tolist() == [88.0, 82.0]


def test_adapter_assigns_round_from_production_rank_without_rescoring():
    scores = [
        _score(f"Player {index}", "RB", "BUF", 100.0 - index, 90.0 - index)
        for index in range(1, 15)
    ]
    population = FantasyRankingPopulation(
        overall=scores,
        by_position={"RB": scores},
        explained_overall=[],
    )

    frame = production_rankings_to_cli_frame(population, teams=12)

    assert frame.loc[0, "suggested_round"] == 1
    assert frame.loc[11, "suggested_round"] == 1
    assert frame.loc[12, "suggested_round"] == 2
    assert frame.loc[13, "suggested_round"] == 2
    assert frame["composite"].tolist() == [score.ranking_score for score in scores]


def test_adapter_rejects_non_positive_team_count():
    population = FantasyRankingPopulation(overall=[], by_position={}, explained_overall=[])

    try:
        production_rankings_to_cli_frame(population, teams=0)
    except ValueError as exc:
        assert str(exc) == "teams must be positive"
    else:
        raise AssertionError("expected ValueError")
