from collections import Counter

from fastapi.testclient import TestClient

from gridiron_gpt.api.app import create_app


def schedule_payload():
    teams = []
    for index in range(1, 11):
        teams.append(
            {
                "team_id": f"team-{index}",
                "name": f"Team {index}",
                "division": "East" if index <= 5 else "West",
            }
        )
    return {
        "teams": teams,
        "regular_season_weeks": 13,
        "playoff_start_week": 14,
        "playoff_weeks": 3,
    }


def test_schedule_endpoint_generates_rrfl_structure(tmp_path):
    response = TestClient(create_app(tmp_path)).post(
        "/schedules/generate",
        json=schedule_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["regular_season_weeks"] == 13
    assert data["playoff_weeks"] == [14, 15, 16]
    assert len(data["matchups"]) == 65


def test_schedule_endpoint_preserves_one_game_per_team_per_week(tmp_path):
    response = TestClient(create_app(tmp_path)).post(
        "/schedules/generate",
        json=schedule_payload(),
    )
    matchups = response.json()["matchups"]

    for week in range(1, 14):
        appearances = Counter()
        for game in matchups:
            if game["week"] == week:
                appearances[game["home_team_id"]] += 1
                appearances[game["away_team_id"]] += 1
        assert len(appearances) == 10
        assert set(appearances.values()) == {1}


def test_schedule_endpoint_rejects_short_regular_season(tmp_path):
    payload = schedule_payload()
    payload["regular_season_weeks"] = 12
    payload["playoff_start_week"] = 13

    response = TestClient(create_app(tmp_path)).post(
        "/schedules/generate",
        json=payload,
    )

    assert response.status_code == 422
    assert "at least 13 weeks" in response.json()["detail"]
