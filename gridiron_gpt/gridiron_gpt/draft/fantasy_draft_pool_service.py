from __future__ import annotations

from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore
from gridiron_gpt.draft.fantasy_ranking_tier_service import FantasyRankingMarketView


def remaining_population(
    population: FantasyRankingPopulation,
    drafted_player_ids: list[str] | set[str] | tuple[str, ...],
) -> FantasyRankingPopulation:
    drafted = set(drafted_player_ids)
    if not drafted:
        return population
    return FantasyRankingPopulation(
        overall=[score for score in population.overall if score.player_id not in drafted],
        by_position={
            position: [score for score in scores if score.player_id not in drafted]
            for position, scores in population.by_position.items()
        },
        explained_overall=[
            item for item in population.explained_overall if item.score.player_id not in drafted
        ],
    )


def best_available_scores(
    population: FantasyRankingPopulation,
    drafted_player_ids: list[str] | set[str] | tuple[str, ...],
    *,
    limit: int = 5,
) -> list[FantasyRankingScore]:
    if limit <= 0:
        return []
    drafted = set(drafted_player_ids)
    return [
        score for score in population.overall if score.player_id not in drafted
    ][:limit]


def best_value_scores(
    population: FantasyRankingPopulation,
    market_views: dict[str, FantasyRankingMarketView],
    drafted_player_ids: list[str] | set[str] | tuple[str, ...],
    *,
    limit: int = 5,
) -> list[FantasyRankingScore]:
    if limit <= 0:
        return []
    drafted = set(drafted_player_ids)
    candidates = [
        score
        for score in population.overall
        if score.player_id not in drafted
        and market_views.get(score.player_id) is not None
        and market_views[score.player_id].draft_value is not None
        and market_views[score.player_id].draft_value > 0
    ]
    candidates.sort(
        key=lambda score: (
            -float(market_views[score.player_id].draft_value),
            market_views[score.player_id].overall_rank,
        )
    )
    return candidates[:limit]
