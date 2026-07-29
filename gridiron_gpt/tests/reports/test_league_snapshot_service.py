from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.rankings.ranking_service import RankingService
from gridiron_cortex.remember.player_scorecard_repository import (
    PlayerScorecardRepository,
)
from gridiron_cortex.reports.league_snapshot_service import (
    LeagueSnapshotService,
)

class FakePlayerScorecardRepository(PlayerScorecardRepository):

    def __init__(self, scorecards):
        self._scorecards = scorecards

    def save(self, scorecard):
        self._scorecards.append(scorecard)

    def get_latest(self, player_id):
        for scorecard in reversed(self._scorecards):
            if scorecard.player_id == player_id:
                return scorecard

        return None

    def get_history(self, player_id):
        return [
            scorecard
            for scorecard in self._scorecards
            if scorecard.player_id == player_id
        ]

    def get_all_latest(self):
        return self._scorecards

def build_scorecard(
    name,
    score,
    position,
):
    return PlayerScorecard(
        player_id=name.lower().replace(" ", "_"),
        player_name=name,
        team="HOU",
        position=position,
        overall_score=score,
    )

def test_empty_snapshot():

    rankings = RankingService(
        FakePlayerScorecardRepository([])
    )

    snapshot = LeagueSnapshotService(
        rankings
    ).build_snapshot()

    assert snapshot.overall == []
    assert snapshot.quarterbacks == []
    assert snapshot.running_backs == []
    assert snapshot.wide_receivers == []
    assert snapshot.tight_ends == []

def test_snapshot_contains_overall_rankings():

    rankings = RankingService(
        FakePlayerScorecardRepository(
            [
                build_scorecard("Player A", 90, "QB"),
                build_scorecard("Player B", 80, "RB"),
            ]
        )
    )

    snapshot = LeagueSnapshotService(
        rankings
    ).build_snapshot()

    assert len(snapshot.overall) == 2
    assert snapshot.overall[0].player_name == "Player A"
    assert snapshot.generated_at.tzinfo is not None

def test_snapshot_separates_positions():

    rankings = RankingService(
        FakePlayerScorecardRepository(
            [
                build_scorecard("QB One", 95, "QB"),
                build_scorecard("RB One", 90, "RB"),
                build_scorecard("WR One", 88, "WR"),
            ]
        )
    )

    snapshot = LeagueSnapshotService(
         rankings
    ).build_snapshot()

    assert len(snapshot.quarterbacks) == 1
    assert len(snapshot.running_backs) == 1
    assert len(snapshot.wide_receivers) == 1


def test_snapshot_respects_limit():

    rankings = RankingService(
        FakePlayerScorecardRepository(
            [
                build_scorecard("A", 100, "QB"),
                build_scorecard("B", 99, "QB"),
                build_scorecard("C", 98, "QB"),
            ]
        )
    )

    snapshot = LeagueSnapshotService(
        rankings
    ).build_snapshot(top_n=2)

    assert len(snapshot.overall) == 2
