from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.rankings.ranking_service import RankingService
from gridiron_cortex.remember.player_scorecard_repository import (
    PlayerScorecardRepository,
)
from gridiron_cortex.enrich.player_enrichment_service import (
    PlayerEnrichmentService,
)
from gridiron_cortex.reasoning.trend_analyzer import TrendAnalyzer
from gridiron_cortex.transforms.player_intelligence_builder import (
    PlayerIntelligenceBuilder,
)

class FakePlayerScorecardRepository(PlayerScorecardRepository):
    def __init__(self, scorecards: list[PlayerScorecard]):
        self.scorecards = scorecards

    def get_all_latest(self) -> list[PlayerScorecard]:
        return self.scorecards

    def get_latest(self, player_id: str) -> PlayerScorecard | None:
        for scorecard in self.scorecards:
            if scorecard.player_id == player_id:
                return scorecard
        return None

    def get_history(self, player_id: str) -> list[PlayerScorecard]:
        latest = self.get_latest(player_id)
        return [latest] if latest else []

    def save(self, scorecard: PlayerScorecard) -> None:
        self.scorecards.append(scorecard)


def build_scorecard(
    player_id: str,
    player_name: str,
    score: float,
    position: str | None = None,
    team: str | None = None,
) -> PlayerScorecard:
    return PlayerScorecard(
        player_id=player_id,
        player_name=player_name,
        team=team,
        position=position,
        overall_score=score,
    )


def test_returns_empty_rankings_when_repository_is_empty():
    repository = FakePlayerScorecardRepository([])

    service = RankingService(repository)

    rankings = service.get_overall_rankings()

    assert rankings == []


def test_overall_rankings_are_sorted_by_score():
    repository = FakePlayerScorecardRepository(
        [
            build_scorecard(
                "tank",
                "Tank Dell",
                82,
                "WR",
                "HOU",
            ),
            build_scorecard(
                "nico",
                "Nico Collins",
                88,
                "WR",
                "HOU",
            ),
            build_scorecard(
                "chase",
                "Ja'Marr Chase",
                95,
                "WR",
                "CIN",
            ),
        ]
    )

    service = RankingService(repository)

    rankings = service.get_overall_rankings()

    assert rankings[0].player_name == "Ja'Marr Chase"
    assert rankings[1].player_name == "Nico Collins"
    assert rankings[2].player_name == "Tank Dell"

    assert rankings[0].rank == 1
    assert rankings[1].rank == 2
    assert rankings[2].rank == 3


def test_position_rankings_only_return_requested_position():
    repository = FakePlayerScorecardRepository(
        [
            build_scorecard(
                "mahomes",
                "Patrick Mahomes",
                95,
                "QB",
                "KC",
            ),
            build_scorecard(
                "allen",
                "Josh Allen",
                93,
                "QB",
                "BUF",
            ),
            build_scorecard(
                "bijan",
                "Bijan Robinson",
                91,
                "RB",
                "ATL",
            ),
            build_scorecard(
                "tank",
                "Tank Dell",
                88,
                "WR",
                "HOU",
            ),
        ]
    )

    service = RankingService(repository)

    rankings = service.get_position_rankings(
        "QB",
        limit=25,
    )

    assert len(rankings) == 2

    assert rankings[0].player_name == "Patrick Mahomes"
    assert rankings[1].player_name == "Josh Allen"

    assert all(
        ranking.position == "QB"
        for ranking in rankings
    )


def test_limit_is_respected():
    repository = FakePlayerScorecardRepository(
        [
            build_scorecard(
                str(i),
                f"Player {i}",
                100 - i,
                "WR",
                "HOU",
            )
            for i in range(10)
        ]
    )

    service = RankingService(repository)

    rankings = service.get_overall_rankings(limit=5)

    assert len(rankings) == 5


def test_players_without_position_are_excluded_from_position_rankings():
    repository = FakePlayerScorecardRepository(
        [
            build_scorecard(
                "tank",
                "Tank Dell",
                90,
                "WR",
                "HOU",
            ),
            build_scorecard(
                "unknown",
                "Mystery Player",
                99,
                None,
                None,
            ),
        ]
    )

    service = RankingService(repository)

    rankings = service.get_position_rankings(
        "WR",
        limit=100,
    )

    assert len(rankings) == 1
    assert rankings[0].player_name == "Tank Dell"


def test_equal_scores_produce_sequential_ranks():
    repository = FakePlayerScorecardRepository(
        [
            build_scorecard(
                "a",
                "Player A",
                90,
                "WR",
                "A",
            ),
            build_scorecard(
                "b",
                "Player B",
                90,
                "WR",
                "B",
            ),
            build_scorecard(
                "c",
                "Player C",
                85,
                "WR",
                "C",
            ),
        ]
    )

    service = RankingService(repository)

    rankings = service.get_overall_rankings()

    assert rankings[0].rank == 1
    assert rankings[1].rank == 2
    assert rankings[2].rank == 3
