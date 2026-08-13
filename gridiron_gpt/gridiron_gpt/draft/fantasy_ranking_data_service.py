from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gridiron_gpt.draft.fetcher import fetch_adp
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulation,
    FantasyRankingPopulationService,
)
from gridiron_gpt.draft.scorer import get_historical_scores


@dataclass(frozen=True)
class AdpSnapshot:
    records: dict[str, dict]
    year: int | None


@dataclass(frozen=True)
class FantasyRankingDataSnapshot:
    population: FantasyRankingPopulation
    historical_player_count: int
    adp_player_count: int
    adp_year: int | None
    adp_used: bool


class FantasyRankingDataService:
    """Load real project data and feed the fantasy-ranking pipeline."""

    def __init__(
        self,
        population_service: FantasyRankingPopulationService,
        *,
        historical_loader: Callable = get_historical_scores,
        adp_loader: Callable = fetch_adp,
        ranking_season: int = 2026,
    ) -> None:
        self.population_service = population_service
        self.historical_loader = historical_loader
        self.adp_loader = adp_loader
        self.ranking_season = ranking_season

    def build(
        self,
        *,
        scoring: str = "ppr",
        teams: int = 12,
        limit: int | None = None,
        role_scores_by_player_id: dict[str, float] | None = None,
        role_provenance_by_player_id: dict[str, str] | None = None,
    ) -> FantasyRankingDataSnapshot:
        historical = self.historical_loader(scoring=scoring)
        historical_points = self._historical_points_by_name(historical)

        adp_snapshot = self._load_adp(
            scoring=scoring,
            teams=teams,
        )

        # Stale market data is unavailable evidence, not negative evidence.
        # The scorer will redistribute the missing market weight.
        adp_is_current = adp_snapshot.year == self.ranking_season

        if adp_is_current:
            adp_by_name = {
                name: float(record["adp"])
                for name, record in adp_snapshot.records.items()
                if record.get("adp") is not None
            }
        else:
            adp_by_name = {}

        draft_pool_size = len(adp_by_name) or None

        population = self.population_service.build(
            historical_points_by_name=historical_points,
            adp_by_name=adp_by_name,
            role_scores_by_player_id=role_scores_by_player_id,
            role_provenance_by_player_id=role_provenance_by_player_id,
            draft_pool_size=draft_pool_size,
            limit=limit,
        )

        return FantasyRankingDataSnapshot(
            population=population,
            historical_player_count=len(historical_points),
            adp_player_count=len(adp_by_name),
            adp_year=adp_snapshot.year,
            adp_used=adp_is_current and bool(adp_by_name),
        )

    def _load_adp(
        self,
        *,
        scoring: str,
        teams: int,
    ) -> AdpSnapshot:
        """Support both legacy and future year-aware ADP loaders."""

        result = self.adp_loader(
            scoring=scoring,
            teams=teams,
        )

        if isinstance(result, AdpSnapshot):
            return result

        # The legacy fetcher returns records but not the successful season.
        # We therefore cannot safely claim those records are 2026 ADP.
        return AdpSnapshot(
            records=result or {},
            year=None,
        )

    @staticmethod
    def _historical_points_by_name(frame) -> dict[str, float]:
        if frame is None or getattr(frame, "empty", True):
            return {}

        required = {
            "player_display_name",
            "hist_score",
        }

        if not required.issubset(frame.columns):
            return {}

        values: dict[str, float] = {}

        for row in frame[
            ["player_display_name", "hist_score"]
        ].itertuples(index=False):
            name = str(row.player_display_name).strip()

            if not name:
                continue

            score = float(row.hist_score)
            values[name] = max(
                score,
                values.get(name, score),
            )

        return values
