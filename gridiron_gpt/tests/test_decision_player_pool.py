from gridiron_gpt.product.decision_player_pool import build_decision_player_pool


def confidence(signals):
    return 80.0 if signals else 0.0


def test_catalog_is_authoritative_and_unscored_fantasy_players_are_kept():
    catalog = [
        {"player": "Alpha QB", "gsis_id": "00-1", "team": "BUF", "position": "QB"},
        {"player": "Beta WR", "gsis_id": "00-2", "team": "HOU", "position": "WR"},
        {"player": "Gamma OL", "gsis_id": "00-3", "team": "DAL", "position": "OL"},
    ]
    score_data = {
        ("Alpha QB", "BUF"): {"score": 6.0, "signals": [{"value": 1.0}]},
    }

    players = build_decision_player_pool(
        catalog,
        score_data,
        confidence_from_signals=confidence,
    )

    assert [player.player_name for player in players] == ["Alpha QB", "Beta WR"]
    assert players[0].player_id == "00-1"
    assert players[0].cortex_score == 6.0
    assert players[0].confidence == 0.8
    assert players[1].player_id == "00-2"
    assert players[1].cortex_score == 0.0
    assert players[1].confidence == 0.0
    assert players[1].projected_points == 10.0


def test_score_lookup_falls_back_to_name_when_team_code_differs():
    catalog = [
        {"player": "Jaguars RB", "gsis_id": "00-4", "team": "JAX", "position": "RB"},
    ]
    score_data = {
        ("Jaguars RB", "JAC"): {"score": 4.0, "signals": []},
    }

    player = build_decision_player_pool(
        catalog,
        score_data,
        confidence_from_signals=confidence,
    )[0]

    assert player.cortex_score == 4.0
    assert player.team == "JAC"


def test_fullback_and_kicker_remain_selectable_for_custom_leagues():
    catalog = [
        {"player": "Full Back", "gsis_id": "00-5", "team": "SF", "position": "FB"},
        {"player": "Field Goal", "gsis_id": "00-6", "team": "BAL", "position": "K"},
    ]

    players = build_decision_player_pool(
        catalog,
        {},
        confidence_from_signals=confidence,
    )

    assert {player.position for player in players} == {"FB", "K"}
