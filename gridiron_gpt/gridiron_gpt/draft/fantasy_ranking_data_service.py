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
    role_player_count: int = 0
    role_season: int | None = None


@dataclass(frozen=True)
class RoleSnapshot:
    scores_by_player_id: dict[str, float]
    provenance_by_player_id: dict[str, str]
    season: int | None


class FantasyRankingDataService:
    """Load real project data and feed the fantasy-ranking pipeline."""

    def __init__(
        self,
        population_service: FantasyRankingPopulationService,
        *,
        historical_loader: Callable = get_historical_scores,
        adp_loader: Callable = fetch_adp,
        role_loader: Callable | None = None,
        ranking_season: int = 2026,
    ) -> None:
        self.population_service = population_service
        self.historical_loader = historical_loader
        self.adp_loader = adp_loader
        self.role_loader = role_loader or self._load_observed_role_snapshot
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

        adp_snapshot = self._load_adp(scoring=scoring, teams=teams)

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
            draft_pool_size=draft_pool_size,
            limit=limit,
        )

        return FantasyRankingDataSnapshot(
            population=population,
            historical_player_count=len(historical_points),
            adp_player_count=len(adp_by_name),
            adp_year=adp_snapshot.year,
            adp_used=adp_is_current and bool(adp_by_name),
            role_player_count=len(role_scores_by_player_id or {}),
            role_season=role_snapshot.season,
        )

    def _load_adp(self, *, scoring: str, teams: int) -> AdpSnapshot:
        """Support both legacy and future year-aware ADP loaders."""
        result = self.adp_loader(scoring=scoring, teams=teams)
        if isinstance(result, AdpSnapshot):
            return result
        return AdpSnapshot(records=result or {}, year=None)

    @staticmethod
    def _load_observed_role_snapshot(*, season: int) -> RoleSnapshot:
        """Derive 0-100 role percentiles from recent observed NFL usage.

        This deliberately uses the latest completed season rather than pretending
        preseason roster labels are depth order. QB opportunity is based on team
        pass-attempt share, RB opportunity on carry/target share, and WR/TE
        opportunity on target share. The raw opportunity metric is converted to a
        within-position percentile so role evidence is comparable on a 0-100 scale.
        """
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

        # Keep a recent sample so the role signal reflects late-season usage more
        # strongly than a player's role from early in the year.
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
            scores[player_id] = float(row.role_score)
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
            score = float(row.hist_score)
            values[name] = max(score, values.get(name, score))
        return values
