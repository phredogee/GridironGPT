from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from gridiron_gpt.draft.fantasy_ranking_data_service import (
    AdpSnapshot,
    FantasyRankingDataService,
    RoleSnapshot,
)


@dataclass
class PopulationResult:
    overall: list
    by_position: dict


class StubPopulationService:
    def __init__(self):
        self.kwargs = None

    def build(self, **kwargs):
        self.kwargs = kwargs
        return PopulationResult(overall=[], by_position={})


def test_build_loads_role_snapshot_when_explicit_role_scores_are_absent():
    population_service = StubPopulationService()

    def historical_loader(*, scoring):
        return pd.DataFrame(
            [{"player_display_name": "Player One", "hist_score": 100.0}]
        )

    def adp_loader(*, scoring, teams):
        return AdpSnapshot(
            records={"Player One": {"adp": 10.0}},
            year=2026,
        )

    def role_loader(*, season):
        assert season == 2025
        return RoleSnapshot(
            scores_by_player_id={"00-TEST": 87.5},
            provenance_by_player_id={"00-TEST": "observed usage test"},
            season=2025,
        )

    service = FantasyRankingDataService(
        population_service,
        historical_loader=historical_loader,
        adp_loader=adp_loader,
        role_loader=role_loader,
        ranking_season=2026,
    )

    snapshot = service.build()

    assert population_service.kwargs["role_scores_by_player_id"] == {
        "00-TEST": 87.5
    }
    assert population_service.kwargs["role_provenance_by_player_id"] == {
        "00-TEST": "observed usage test"
    }
    assert snapshot.role_player_count == 1
    assert snapshot.role_season == 2025


def test_explicit_role_scores_bypass_role_loader():
    population_service = StubPopulationService()

    def historical_loader(*, scoring):
        return pd.DataFrame()

    def adp_loader(*, scoring, teams):
        return AdpSnapshot(records={}, year=None)

    def role_loader(*, season):
        raise AssertionError("role loader should not be called")

    service = FantasyRankingDataService(
        population_service,
        historical_loader=historical_loader,
        adp_loader=adp_loader,
        role_loader=role_loader,
    )

    snapshot = service.build(
        role_scores_by_player_id={"00-TEST": 75.0},
        role_provenance_by_player_id={"00-TEST": "manual role"},
    )

    assert population_service.kwargs["role_scores_by_player_id"] == {
        "00-TEST": 75.0
    }
    assert snapshot.role_player_count == 1
    assert snapshot.role_season is None


def test_multiple_current_adp_sources_feed_consensus_market_value():
    population_service = StubPopulationService()

    def historical_loader(*, scoring):
        return pd.DataFrame()

    def adp_loader(*, scoring, teams):
        return AdpSnapshot(
            records={"Player One": {"adp": 10.0}},
            year=2026,
        )

    service = FantasyRankingDataService(
        population_service,
        historical_loader=historical_loader,
        adp_loader=adp_loader,
        adp_source_loaders={
            "NFL Fantasy": lambda: {"Player One": 6.0},
        },
        ranking_season=2026,
    )

    snapshot = service.build(role_scores_by_player_id={})

    assert population_service.kwargs["adp_by_name"] == {"Player One": 8.0}
    assert snapshot.adp_player_count == 1
    assert snapshot.adp_sources == (
        "Fantasy Football Calculator",
        "NFL Fantasy",
    )
    market = next(iter(snapshot.consensus_adp_by_key.values()))
    assert market.consensus_adp == 8.0
    assert market.adp_spread == 4.0
    assert market.source_count == 2


def test_current_secondary_adp_can_replace_stale_primary_market_data():
    population_service = StubPopulationService()

    def historical_loader(*, scoring):
        return pd.DataFrame()

    def adp_loader(*, scoring, teams):
        return AdpSnapshot(
            records={"Player One": {"adp": 30.0}},
            year=2024,
        )

    service = FantasyRankingDataService(
        population_service,
        historical_loader=historical_loader,
        adp_loader=adp_loader,
        adp_source_loaders={
            "NFL Fantasy": lambda: {"Player One": 7.0},
        },
        ranking_season=2026,
    )

    snapshot = service.build(role_scores_by_player_id={})

    assert population_service.kwargs["adp_by_name"] == {"Player One": 7.0}
    assert snapshot.adp_year == 2026
    assert snapshot.adp_used is True
    assert snapshot.adp_sources == ("NFL Fantasy",)
