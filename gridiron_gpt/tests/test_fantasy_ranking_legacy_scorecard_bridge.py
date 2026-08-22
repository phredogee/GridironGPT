from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulationService,
)
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


class StubPlayerRepository:
    def all_latest(self):
        return [
            CanonicalPlayerState(
                player_id="00-0039999",
                player_name="Tank Dell",
                team="HOU",
                position="WR",
                roster_status="ACT",
            )
        ]


class LegacyScorecardRepository:
    def get_latest(self, player_id):
        return None

    def get_all_latest(self):
        return [
            PlayerScorecard(
                player_id="tank_dell",
                player_name="Tank Dell",
                team="HOU",
                position="WR",
                overall_score=58.0,
            )
        ]


def test_legacy_scorecard_matches_by_normalized_name_and_team():
    service = FantasyRankingPopulationService(
        StubPlayerRepository(),
        LegacyScorecardRepository(),
    )

    result = service.build(
        historical_points_by_name={"Tank Dell": 100.0},
    )

    assert len(result.overall) == 1
    assert result.overall[0].components["cortex"] == 58.0
