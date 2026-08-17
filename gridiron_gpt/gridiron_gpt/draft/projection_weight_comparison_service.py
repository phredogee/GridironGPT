from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.draft.fantasy_projection_view_service import FantasyProjectionView
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation


@dataclass(frozen=True)
class ProjectionWeightComparison:
    player_id: str
    player_name: str
    position: str | None
    team: str | None
    production_rank: int
    production_score: float
    projected_points: float | None
    projection_score: float | None
    rank_5: int
    score_5: float
    movement_5: int
    rank_10: int
    score_10: float
    movement_10: int


class ProjectionWeightComparisonService:
    """Compare hypothetical projection weights without mutating production rankings.

    The existing ranking score remains the 0% control. Projected fantasy points
    are normalized to 0-100 against the maximum projection in the ranked pool.
    Experimental scores reserve 5% or 10% for projection and proportionally
    scale the complete production score into the remaining weight.
    """

    WEIGHTS = (0.05, 0.10)

    def compare(
        self,
        population: FantasyRankingPopulation,
        projection_views: dict[str, FantasyProjectionView],
    ) -> list[ProjectionWeightComparison]:
        production = list(population.overall)
        if not production:
            return []

        projections = {
            score.player_id: projection_views.get(score.player_name.casefold())
            for score in production
        }
        available_points = [
            view.projected_points
            for view in projections.values()
            if view is not None and view.projected_points >= 0
        ]
        maximum = max(available_points, default=0.0)

        projection_scores = {
            player_id: self._normalize_projection(view, maximum)
            for player_id, view in projections.items()
        }
        experimental = {
            weight: self._experimental_scores(production, projection_scores, weight)
            for weight in self.WEIGHTS
        }
        ranks = {
            weight: self._ranks(production, scores)
            for weight, scores in experimental.items()
        }

        rows: list[ProjectionWeightComparison] = []
        for production_rank, score in enumerate(production, start=1):
            view = projections[score.player_id]
            score_5 = experimental[0.05][score.player_id]
            score_10 = experimental[0.10][score.player_id]
            rank_5 = ranks[0.05][score.player_id]
            rank_10 = ranks[0.10][score.player_id]
            rows.append(
                ProjectionWeightComparison(
                    player_id=score.player_id,
                    player_name=score.player_name,
                    position=score.position,
                    team=score.team,
                    production_rank=production_rank,
                    production_score=score.ranking_score,
                    projected_points=view.projected_points if view else None,
                    projection_score=projection_scores[score.player_id],
                    rank_5=rank_5,
                    score_5=score_5,
                    movement_5=production_rank - rank_5,
                    rank_10=rank_10,
                    score_10=score_10,
                    movement_10=production_rank - rank_10,
                )
            )
        return rows

    @staticmethod
    def _normalize_projection(
        view: FantasyProjectionView | None,
        maximum: float,
    ) -> float | None:
        if view is None or maximum <= 0:
            return None
        return round(max(0.0, min(100.0, view.projected_points / maximum * 100.0)), 3)

    @staticmethod
    def _experimental_scores(production, projection_scores, weight: float) -> dict[str, float]:
        result: dict[str, float] = {}
        for score in production:
            projection_score = projection_scores[score.player_id]
            if projection_score is None:
                result[score.player_id] = score.ranking_score
            else:
                result[score.player_id] = round(
                    score.ranking_score * (1.0 - weight) + projection_score * weight,
                    3,
                )
        return result

    @staticmethod
    def _ranks(production, scores: dict[str, float]) -> dict[str, int]:
        ordered = sorted(
            production,
            key=lambda row: (-scores[row.player_id], row.player_name.casefold()),
        )
        return {row.player_id: rank for rank, row in enumerate(ordered, start=1)}
