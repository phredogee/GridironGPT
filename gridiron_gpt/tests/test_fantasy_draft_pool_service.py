from gridiron_gpt.draft.fantasy_draft_pool_service import (
    best_available_scores,
    best_value_scores,
    remaining_population,
)
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore
from gridiron_gpt.draft.fantasy_ranking_tier_service import FantasyRankingMarketView


def _score(player_id: str, ranking_score: float, position: str = "RB") -> FantasyRankingScore:
    return FantasyRankingScore(
        player_id=player_id,
        player_name=player_id.title(),
        team="BUF",
        position=position,
        ranking_score=ranking_score,
        components={"baseline": ranking_score},
        weighted_components={"baseline": ranking_score},
        provenance={},
    )


def _population(scores: list[FantasyRankingScore]) -> FantasyRankingPopulation:
    return FantasyRankingPopulation(
        overall=scores,
        by_position={"RB": [score for score in scores if score.position == "RB"]},
        explained_overall=[],
    )


def _market(player_id: str, overall_rank: int, draft_value: float | None) -> FantasyRankingMarketView:
    return FantasyRankingMarketView(
        player_id=player_id,
        overall_rank=overall_rank,
        position_rank=overall_rank,
        tier=1,
        consensus_adp=None,
        adp_source_count=0,
        adp_spread=None,
        draft_value=draft_value,
        source_adps={},
    )


def test_best_available_removes_drafted_players_and_preserves_board_order():
    scores = [_score("alpha", 95.0), _score("bravo", 90.0), _score("charlie", 85.0)]
    population = _population(scores)

    available = best_available_scores(population, ["alpha"], limit=2)

    assert [score.player_id for score in available] == ["bravo", "charlie"]


def test_best_value_removes_drafted_players_and_orders_by_positive_draft_value():
    scores = [_score("alpha", 95.0), _score("bravo", 90.0), _score("charlie", 85.0)]
    population = _population(scores)
    market_views = {
        "alpha": _market("alpha", 1, 12.0),
        "bravo": _market("bravo", 2, 8.0),
        "charlie": _market("charlie", 3, 10.0),
    }

    values = best_value_scores(population, market_views, ["alpha"], limit=5)

    assert [score.player_id for score in values] == ["charlie", "bravo"]


def test_best_value_excludes_non_positive_or_missing_value():
    scores = [_score("alpha", 95.0), _score("bravo", 90.0), _score("charlie", 85.0)]
    population = _population(scores)
    market_views = {
        "alpha": _market("alpha", 1, 0.0),
        "bravo": _market("bravo", 2, -2.0),
        "charlie": _market("charlie", 3, None),
    }

    assert best_value_scores(population, market_views, [], limit=5) == []


def test_remaining_population_filters_overall_and_position_lists():
    scores = [_score("alpha", 95.0), _score("bravo", 90.0)]
    population = _population(scores)

    remaining = remaining_population(population, {"alpha"})

    assert [score.player_id for score in remaining.overall] == ["bravo"]
    assert [score.player_id for score in remaining.by_position["RB"]] == ["bravo"]


def test_non_positive_limits_return_empty_lists():
    scores = [_score("alpha", 95.0)]
    population = _population(scores)

    assert best_available_scores(population, [], limit=0) == []
    assert best_value_scores(population, {"alpha": _market("alpha", 1, 5.0)}, [], limit=0) == []
