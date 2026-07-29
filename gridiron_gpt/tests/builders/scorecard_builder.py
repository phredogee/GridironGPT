from gridiron_cortex.models.player_scorecard import PlayerScorecard


def build_scorecard(
    player_name: str = "Tank Dell",
    *,
    player_id: str | None = None,
    team: str = "HOU",
    position: str = "WR",
    overall_score: float = 50.0,
) -> PlayerScorecard:
    return PlayerScorecard(
        player_id=player_id
        or player_name.lower().replace(" ", "_"),
        player_name=player_name,
        team=team,
        position=position,
        overall_score=overall_score,
    )
