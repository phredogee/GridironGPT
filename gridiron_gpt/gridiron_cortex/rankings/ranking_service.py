from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.ranking_entry import RankingEntry
from gridiron_cortex.remember.player_scorecard_repository import (
    PlayerScorecardRepository,
)

class RankingService:

    def __init__(
        self,
        repository: PlayerScorecardRepository,
    ):
        self.repository = repository

    def get_overall_rankings(
        self,
        limit: int = 200,
    ) -> list[PlayerScorecard]:

        ordered = sorted(
            self.repository.get_all_latest(),
            key=lambda scorecard: scorecard.overall_score,
            reverse=True,
        )

        return self._to_ranking_entries(ordered[:limit])

    def get_position_rankings(
        self,
        position: str,
        limit: int,
    ) -> list[RankingEntry]:

        filtered = [
            scorecard
            for scorecard in self.repository.get_all_latest()
            if scorecard.position == position
        ]

        ordered = sorted(
            filtered,
            key=lambda scorecard: scorecard.overall_score,
            reverse=True,
        )

        return self._to_ranking_entries(ordered[:limit])

    def _to_ranking_entries(
        self,
        scorecards: list[PlayerScorecard],
    ) -> list[RankingEntry]:

        rankings = []

        for rank, scorecard in enumerate(scorecards, start=1):
            rankings.append(
                RankingEntry(
                    rank=rank,
                    player_id=scorecard.player_id,
                    player_name=scorecard.player_name,
                    team=scorecard.team,
                    position=scorecard.position,
                    overall_score=scorecard.overall_score,
                )
            )

        return rankings
