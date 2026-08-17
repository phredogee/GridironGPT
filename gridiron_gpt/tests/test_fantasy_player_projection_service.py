from gridiron_gpt.draft.fantasy_player_projection_service import (
    FantasyPlayerProjectionService,
)
from gridiron_gpt.draft.fantasy_projection_service import (
    FantasyProjectionService,
    PlayerStatProjection,
)


class StubStatProjectionService:
    def __init__(self, projections):
        self.projections = projections
        self.kwargs = None

    def build(self, **kwargs):
        self.kwargs = kwargs
        return dict(self.projections)


def test_build_connects_stat_projection_to_fantasy_points():
    stat_service = StubStatProjectionService({
        "Player One": PlayerStatProjection(
            games=17,
            rushing_yards=1000,
            rushing_touchdowns=10,
            receptions=60,
            receiving_yards=500,
            receiving_touchdowns=3,
            fumbles_lost=2,
        )
    })
    service = FantasyPlayerProjectionService(
        stat_projection_service=stat_service,
        fantasy_projection_service=FantasyProjectionService(),
    )

    projections = service.build(scoring="ppr", expected_games=16)

    projection = projections["Player One"]
    assert projection.player_name == "Player One"
    assert projection.fantasy.projected_points == 284.0
    assert projection.fantasy.projected_ppg == 16.71
    assert stat_service.kwargs == {"seasons": None, "expected_games": 16}


def test_build_respects_scoring_format():
    stats = PlayerStatProjection(games=10, receptions=40, receiving_yards=600)
    service = FantasyPlayerProjectionService(
        stat_projection_service=StubStatProjectionService({"Receiver": stats})
    )

    standard = service.build(scoring="standard")["Receiver"]
    ppr = service.build(scoring="ppr")["Receiver"]

    assert standard.fantasy.projected_points == 60.0
    assert ppr.fantasy.projected_points == 100.0


def test_ranked_orders_players_by_projected_points():
    service = FantasyPlayerProjectionService(
        stat_projection_service=StubStatProjectionService({
            "Lower": PlayerStatProjection(games=17, rushing_yards=500),
            "Higher": PlayerStatProjection(games=17, rushing_yards=1000),
        })
    )

    ranked = service.ranked(scoring="standard")

    assert [projection.player_name for projection in ranked] == ["Higher", "Lower"]


def test_empty_stat_projection_returns_empty_outputs():
    service = FantasyPlayerProjectionService(
        stat_projection_service=StubStatProjectionService({})
    )

    assert service.build() == {}
    assert service.ranked() == []
