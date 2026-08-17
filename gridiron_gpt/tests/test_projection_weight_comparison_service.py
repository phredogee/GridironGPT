from gridiron_gpt.draft.fantasy_projection_view_service import FantasyProjectionView
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore
from gridiron_gpt.draft.projection_weight_comparison_service import ProjectionWeightComparisonService


def _score(player_id: str, name: str, ranking_score: float) -> FantasyRankingScore:
    return FantasyRankingScore(
        player_id=player_id,
        player_name=name,
        team="TST",
        position="RB",
        ranking_score=ranking_score,
        components={"baseline": ranking_score},
        weighted_components={"baseline": ranking_score},
        provenance={},
    )


def _population(*scores: FantasyRankingScore) -> FantasyRankingPopulation:
    return FantasyRankingPopulation(
        overall=list(scores),
        by_position={"RB": list(scores)},
        explained_overall=[],
    )


def _view(points: float) -> FantasyProjectionView:
    return FantasyProjectionView(
        projected_points=points,
        projected_ppg=points / 17.0,
    )


def test_projection_points_are_normalized_to_ranked_pool_maximum():
    population = _population(
        _score("one", "Player One", 90.0),
        _score("two", "Player Two", 80.0),
    )
    views = {
        "player one": _view(400.0),
        "player two": _view(200.0),
    }

    rows = ProjectionWeightComparisonService().compare(population, views)

    assert rows[0].projection_score == 100.0
    assert rows[1].projection_score == 50.0
    assert rows[0].production_score == 90.0


def test_projection_weight_can_change_rank_without_mutating_production_order():
    population = _population(
        _score("one", "Player One", 90.0),
        _score("two", "Player Two", 89.0),
    )
    views = {
        "player one": _view(200.0),
        "player two": _view(400.0),
    }

    rows = ProjectionWeightComparisonService().compare(population, views)
    by_id = {row.player_id: row for row in rows}

    assert [score.player_id for score in population.overall] == ["one", "two"]
    assert by_id["one"].production_rank == 1
    assert by_id["two"].production_rank == 2
    assert by_id["two"].rank_5 == 1
    assert by_id["two"].movement_5 == 1
    assert by_id["two"].rank_10 == 1
    assert by_id["one"].movement_10 == -1


def test_missing_projection_does_not_penalize_production_score():
    population = _population(
        _score("one", "Player One", 88.0),
        _score("two", "Player Two", 80.0),
    )
    views = {"player two": _view(300.0)}

    rows = ProjectionWeightComparisonService().compare(population, views)
    first = rows[0]

    assert first.player_id == "one"
    assert first.projection_score is None
    assert first.score_5 == 88.0
    assert first.score_10 == 88.0


def test_empty_population_returns_empty_comparison():
    population = FantasyRankingPopulation(overall=[], by_position={}, explained_overall=[])

    assert ProjectionWeightComparisonService().compare(population, {}) == []
