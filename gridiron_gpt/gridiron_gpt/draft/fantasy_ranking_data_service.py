from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Callable

from gridiron_gpt.draft.consensus_adp_service import (
    ConsensusAdpRecord,
    ConsensusAdpService,
)
from gridiron_gpt.draft.fetcher import fetch_adp
from gridiron_gpt.draft.fantasy_player_projection_service import FantasyPlayerProjectionService
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulation,
    FantasyRankingPopulationService,
)
from gridiron_gpt.draft.fantasy_ranking_tier_service import (
    FantasyRankingMarketView,
    FantasyRankingTierService,
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
    role_player_count: int = 0
    role_season: int | None = None
    consensus_adp_by_key: dict[str, ConsensusAdpRecord] = field(default_factory=dict)
    market_views_by_player_id: dict[str, FantasyRankingMarketView] = field(default_factory=dict)
    adp_sources: tuple[str, ...] = ()
    projection_player_count: int = 0


@dataclass(frozen=True)
class RoleSnapshot:
    scores_by_player_id: dict[str, float]
    provenance_by_player_id: dict[str, str]
    season: int | None


class FantasyRankingDataService:
    """Load real project data and feed the fantasy-ranking pipeline."""

    PRIMARY_ADP_SOURCE = "Fantasy Football Calculator"
    MARKET_DRAFT_POOL_SIZE = 256

    def __init__(
        self,
        population_service: FantasyRankingPopulationService,
        *,
        historical_loader: Callable = get_historical_scores,
        adp_loader: Callable = fetch_adp,
        role_loader: Callable | None = None,
        projection_loader: Callable | None = None,
        adp_source_loaders: dict[str, Callable] | None = None,
        consensus_adp_service: ConsensusAdpService | None = None,
        tier_service: FantasyRankingTierService | None = None,
        ranking_season: int = 2026,
    ) -> None:
        self.population_service = population_service
        self.historical_loader = historical_loader
        self.adp_loader = adp_loader
        self.role_loader = role_loader or self._load_observed_role_snapshot
        self.projection_loader = projection_loader or FantasyPlayerProjectionService().build
        self.adp_source_loaders = (
            self._default_runtime_adp_source_loaders(season=ranking_season)
            if adp_source_loaders is None
            else dict(adp_source_loaders)
        )
        self.consensus_adp_service = consensus_adp_service or ConsensusAdpService()
        self.tier_service = tier_service or FantasyRankingTierService()
        self.ranking_season = ranking_season

    @staticmethod
    def _default_runtime_adp_source_loaders(*, season: int) -> dict[str, Callable]:
        from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader

        espn = EspnAdpLoader(season=season)
        return {"ESPN": espn.load}

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

        try:
            projections = self.projection_loader(scoring=scoring)
        except Exception:
            projections = {}
        projected_points_by_name = {
            str(name): float(projection.projected_points)
            for name, projection in (projections or {}).items()
            if getattr(projection, "projected_points", None) is not None
            and self._finite_nonnegative(getattr(projection, "projected_points", None)) is not None
        }

        primary_snapshot = self._load_adp(scoring=scoring, teams=teams)
        sources = self._adp_sources(primary_snapshot)
        consensus_adp_by_key = self.consensus_adp_service.build(sources)

        adp_by_name = {
            record.player_name: record.consensus_adp
            for record in consensus_adp_by_key.values()
        }
        draft_pool_size = (
            min(len(adp_by_name), self.MARKET_DRAFT_POOL_SIZE)
            if adp_by_name
            else None
        )

        role_snapshot = RoleSnapshot({}, {}, None)
        if role_scores_by_player_id is None:
            role_snapshot = self.role_loader(season=self.ranking_season - 1)
            role_scores_by_player_id = role_snapshot.scores_by_player_id
            if role_provenance_by_player_id is None:
                role_provenance_by_player_id = role_snapshot.provenance_by_player_id

        population = self.population_service.build(
            historical_points_by_name=historical_points,
            adp_by_name=adp_by_name,
            role_scores_by_player_id=role_scores_by_player_id,
            role_provenance_by_player_id=role_provenance_by_player_id,
            projected_points_by_name=projected_points_by_name,
            draft_pool_size=draft_pool_size,
            limit=limit,
        )
        market_views = self.tier_service.build(
            population.overall,
            consensus_adp_by_key=consensus_adp_by_key,
        )

        source_names = tuple(sorted(sources))
        adp_year = self.ranking_season if adp_by_name else primary_snapshot.year

        return FantasyRankingDataSnapshot(
            population=population,
            historical_player_count=len(historical_points),
            adp_player_count=len(adp_by_name),
            adp_year=adp_year,
            adp_used=bool(adp_by_name),
            role_player_count=len(role_scores_by_player_id or {}),
            role_season=role_snapshot.season,
            consensus_adp_by_key=consensus_adp_by_key,
            market_views_by_player_id=market_views,
            adp_sources=source_names,
            projection_player_count=len(projected_points_by_name),
        )

    def _adp_sources(self, primary_snapshot: AdpSnapshot) -> dict[str, dict[str, float]]:
        sources: dict[str, dict[str, float]] = {}

        if primary_snapshot.year == self.ranking_season:
            primary_values = {
                name: float(record["adp"])
                for name, record in primary_snapshot.records.items()
                if record.get("adp") is not None
                and self._finite_positive(record.get("adp")) is not None
            }
            if primary_values:
                sources[self.PRIMARY_ADP_SOURCE] = primary_values

        for source_name, loader in self.adp_source_loaders.items():
            try:
                result = loader()
            except Exception:
                continue

            records = getattr(result, "records", result) or {}
            values: dict[str, float] = {}
            for name, raw_value in records.items():
                if isinstance(raw_value, dict):
                    raw_value = raw_value.get("adp")
                value = self._finite_positive(raw_value)
                if value is not None:
                    values[str(name)] = value
            if values:
                sources[str(source_name)] = values

        return sources

    @staticmethod
    def _finite_positive(value) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(numeric) or numeric <= 0:
            return None
        return numeric

    @staticmethod
    def _finite_nonnegative(value) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(numeric) or numeric < 0:
            return None
        return numeric

    def _load_adp(self, *, scoring: str, teams: int) -> AdpSnapshot:
        result = self.adp_loader(scoring=scoring, teams=teams)
        if isinstance(result, AdpSnapshot):
            return result
        return AdpSnapshot(records=result or {}, year=None)

    @staticmethod
    def _load_observed_role_snapshot(*, season: int) -> RoleSnapshot:
        try:
            import nflreadpy as nfl

            frame = nfl.load_player_stats(seasons=[season])
            if hasattr(frame, "to_pandas"):
                frame = frame.to_pandas()
        except Exception:
            return RoleSnapshot({}, {}, None)

        if frame is None or getattr(frame, "empty", True):
            return RoleSnapshot({}, {}, None)

        required = {"player_id", "position", "week"}
        if not required.issubset(frame.columns):
            return RoleSnapshot({}, {}, None)

        team_col = "recent_team" if "recent_team" in frame.columns else "team"
        if team_col not in frame.columns:
            return RoleSnapshot({}, {}, None)

        work = frame.copy()
        work = work[work["position"].isin(["QB", "RB", "WR", "TE"])]
        work = work[work["player_id"].notna()]
        if work.empty:
            return RoleSnapshot({}, {}, None)

        max_week = work["week"].max()
        work = work[work["week"] >= max(1, int(max_week) - 5)].copy()

        for column in ("attempts", "carries", "targets"):
            if column not in work.columns:
                work[column] = 0.0
            work[column] = work[column].fillna(0.0).astype(float)

        group_keys = ["season", "week", team_col] if "season" in work.columns else ["week", team_col]
        work["team_attempts"] = work.groupby(group_keys)["attempts"].transform("sum")
        work["team_carries"] = work.groupby(group_keys)["carries"].transform("sum")
        work["team_targets"] = work.groupby(group_keys)["targets"].transform("sum")

        def safe_share(numerator, denominator):
            return numerator.where(denominator > 0, 0.0) / denominator.where(denominator > 0, 1.0)

        work["attempt_share"] = safe_share(work["attempts"], work["team_attempts"])
        work["carry_share"] = safe_share(work["carries"], work["team_carries"])
        work["target_share_calc"] = safe_share(work["targets"], work["team_targets"])

        work["role_metric"] = 0.0
        qb = work["position"] == "QB"
        rb = work["position"] == "RB"
        receiver = work["position"].isin(["WR", "TE"])
        work.loc[qb, "role_metric"] = work.loc[qb, "attempt_share"]
        work.loc[rb, "role_metric"] = (
            work.loc[rb, "carry_share"] + work.loc[rb, "target_share_calc"]
        ) / 2.0
        work.loc[receiver, "role_metric"] = work.loc[receiver, "target_share_calc"]

        summary = (
            work.groupby(["player_id", "position"], as_index=False)
            .agg(role_metric=("role_metric", "mean"))
        )
        summary["role_score"] = (
            summary.groupby("position")["role_metric"]
            .rank(method="average", pct=True)
            .mul(100.0)
        )

        scores: dict[str, float] = {}
        provenance: dict[str, str] = {}
        for row in summary.itertuples(index=False):
            player_id = str(row.player_id).strip()
            if not player_id:
                continue
            score = float(row.role_score)
            if not math.isfinite(score):
                continue
            scores[player_id] = score
            provenance[player_id] = (
                f"{season} recent observed usage percentile for {row.position} "
                "(last six available weeks)"
            )

        return RoleSnapshot(scores, provenance, season)

    @staticmethod
    def _historical_points_by_name(frame) -> dict[str, float]:
        if frame is None or getattr(frame, "empty", True):
            return {}

        required = {"player_display_name", "hist_score"}
        if not required.issubset(frame.columns):
            return {}

        values: dict[str, float] = {}
        for row in frame[["player_display_name", "hist_score"]].itertuples(index=False):
            name = str(row.player_display_name).strip()
            if not name:
                continue

            try:
                score = float(row.hist_score)
            except (TypeError, ValueError):
                continue

            if not math.isfinite(score):
                continue

            previous = values.get(name)
            if previous is None or score > previous:
                values[name] = score

        return values
