from datetime import datetime, timezone
from gridiron_cortex.models.league_snapshot import LeagueSnapshot
from gridiron_cortex.rankings.ranking_service import RankingService


class LeagueSnapshotService:

    def __init__(
        self,
        ranking_service: RankingService,
    ):
        self.rankings = ranking_service

    def build_snapshot(
        self,
        top_n: int = 10,
    ) -> LeagueSnapshot:

        return LeagueSnapshot(
            overall=self.rankings.get_overall_rankings(
                limit=top_n,
            ),
            quarterbacks=self.rankings.get_position_rankings(
                "QB",
                limit=top_n,
            ),
            running_backs=self.rankings.get_position_rankings(
                "RB",
                limit=top_n,
            ),
            wide_receivers=self.rankings.get_position_rankings(
                "WR",
                limit=top_n,
            ),
            tight_ends=self.rankings.get_position_rankings(
                "TE",
                limit=top_n,
            ),
            generated_at=datetime.now(timezone.utc),
        )
