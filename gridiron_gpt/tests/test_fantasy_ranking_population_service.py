from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulationService,
)
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


class StubPlayerRepository:
    def __init__(self, players):
        self.players = players

    def all_latest(self):
        return list(self.players)


class StubScorecardRepository:
    def __init__(self, scorecards=None):
        self.scorecards = scorecards or {}

    def get_latest(self, player_id):
        return self.scorecards.get(player_id)


def player(player_id, name, position, status="ACT"):
    return CanonicalPlayerState(
        player_id=player_id,
        player_name=name,
        team="TST",
        position=position,
        roster_status=status,
    )


def test_builds_overall_rankings_from_draftable_skill_positions():
    players = [
        player("p1", "Alpha RB", "RB"),
        player("p2", "Bravo WR", "WR"),
        player("p3", "Charlie OL", "OL"),
    ]
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(),
    )

    result = service.build(
        historical_points_by_name={
            "Alpha RB": 300.0,
            "Bravo WR": 200.0,
            "Charlie OL": 500.0,
        },
    )

    assert [row.player_name for row in result.overall] == [
        "Alpha RB",
        "Bravo WR",
    ]


def test_excludes_retired_and_released_players():
    players = [
        player("p1", "Active RB", "RB", "ACT"),
        player("p2", "Retired RB", "RB", "RET"),
        player("p3", "Released WR", "WR", "CUT"),
    ]
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(),
    )

    result = service.build(
        historical_points_by_name={
            "Active RB": 200.0,
            "Retired RB": 400.0,
            "Released WR": 350.0,
        },
    )

    assert [row.player_name for row in result.overall] == ["Active RB"]


def test_builds_position_lists_from_same_ranked_population():
    players = [
        player("qb1", "QB One", "QB"),
        player("rb1", "RB One", "RB"),
        player("wr1", "WR One", "WR"),
        player("te1", "TE One", "TE"),
    ]
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(),
    )

    result = service.build(
        historical_points_by_name={
            "QB One": 400.0,
            "RB One": 350.0,
            "WR One": 300.0,
            "TE One": 250.0,
        },
    )

    assert [row.player_name for row in result.by_position["QB"]] == ["QB One"]
    assert [row.player_name for row in result.by_position["RB"]] == ["RB One"]
    assert [row.player_name for row in result.by_position["WR"]] == ["WR One"]
    assert [row.player_name for row in result.by_position["TE"]] == ["TE One"]


def test_cortex_and_adp_can_adjust_order_without_replacing_baseline():
    players = [
        player("p1", "Player A", "WR"),
        player("p2", "Player B", "WR"),
    ]
    scorecards = {
        "p1": PlayerScorecard(
            player_id="p1",
            player_name="Player A",
            position="WR",
            overall_score=40.0,
        ),
        "p2": PlayerScorecard(
            player_id="p2",
            player_name="Player B",
            position="WR",
            overall_score=90.0,
        ),
    }
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(scorecards),
    )

    result = service.build(
        historical_points_by_name={"Player A": 300.0, "Player B": 285.0},
        adp_by_name={"Player A": 25.0, "Player B": 5.0},
        draft_pool_size=120,
    )

    assert result.overall[0].player_name == "Player B"
    assert result.overall[0].components["baseline"] < 100.0
    assert result.overall[0].components["market"] > result.overall[1].components["market"]


def test_availability_only_player_is_excluded_without_primary_evidence():
    players = [player("p1", "Unknown Market RB", "RB")]
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(),
    )

    result = service.build()

    assert result.overall == []
    assert result.by_position["RB"] == []


def test_limit_applies_to_overall_population_and_position_views():
    players = [
        player("p1", "A RB", "RB"),
        player("p2", "B RB", "RB"),
        player("p3", "C WR", "WR"),
    ]
    service = FantasyRankingPopulationService(
        StubPlayerRepository(players),
        StubScorecardRepository(),
    )

    result = service.build(
        historical_points_by_name={"A RB": 300, "B RB": 250, "C WR": 200},
        limit=2,
    )

    assert len(result.overall) == 2
    assert [row.player_name for row in result.by_position["RB"]] == ["A RB", "B RB"]
    assert result.by_position["WR"] == []
