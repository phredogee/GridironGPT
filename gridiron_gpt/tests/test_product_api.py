from fastapi.testclient import TestClient

from gridiron_gpt.api.app import create_app


def player(name, position="RB", projected=12.0):
    return {
        "player_id": name.lower().replace(" ", "-"),
        "player_name": name,
        "position": position,
        "team": "ATL",
        "cortex_score": 10.0,
        "confidence": 0.8,
        "projected_points": projected,
        "replacement_value": 2.0,
    }


def league_payload():
    return {
        "league_id": "rrfl",
        "name": "Riff Raff Footbrawl League",
        "teams": 10,
        "roster_size": 15,
        "starting_slots": {"QB": 1, "RB": 2, "WR": 3, "FLEX": 1, "DST": 1},
        "bench_slots": 7,
        "ir_slots": 2,
        "faab_budget": 100,
        "scoring_format": "standard",
    }


def test_health_endpoint(tmp_path):
    response = TestClient(create_app(tmp_path)).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_league_crud(tmp_path):
    client = TestClient(create_app(tmp_path))
    assert client.post("/leagues", json=league_payload()).status_code == 200
    loaded = client.get("/leagues/rrfl")
    assert loaded.status_code == 200
    assert loaded.json()["teams"] == 10
    assert len(client.get("/leagues").json()) == 1
    assert client.delete("/leagues/rrfl").json() == {"deleted": True}


def test_unknown_league_returns_404(tmp_path):
    response = TestClient(create_app(tmp_path)).get("/leagues/missing")
    assert response.status_code == 404


def test_draft_endpoint_returns_ranked_decisions(tmp_path):
    client = TestClient(create_app(tmp_path))
    client.post("/leagues", json=league_payload())
    response = client.post(
        "/decisions/draft/rrfl",
        json={"players": [player("Low", projected=8), player("High", projected=18)]},
    )
    assert response.status_code == 200
    decisions = response.json()
    assert decisions[0]["player_name"] == "High"
    assert decisions[0]["metadata"]["rank"] == 1


def test_start_sit_endpoint(tmp_path):
    response = TestClient(create_app(tmp_path)).post(
        "/decisions/start-sit",
        json={"players": [player("One", projected=18), player("Two", projected=8)], "slots": 1},
    )
    assert response.status_code == 200
    actions = {item["player_name"]: item["action"] for item in response.json()}
    assert actions["One"] == "start"
    assert actions["Two"] == "sit"


def test_waiver_trade_and_roster_endpoints(tmp_path):
    client = TestClient(create_app(tmp_path))
    client.post("/leagues", json=league_payload())

    waiver = client.post(
        "/decisions/waivers",
        json={
            "league_id": "rrfl",
            "free_agents": [player("TE Target", "TE", 15)],
            "roster": [player("QB", "QB"), player("RB", "RB")],
        },
    )
    assert waiver.status_code == 200
    assert waiver.json()[0]["action"] == "add"

    trade = client.post(
        "/decisions/trade",
        json={"give": [player("Give", projected=8)], "receive": [player("Receive", projected=18)]},
    )
    assert trade.status_code == 200
    assert trade.json()["action"] == "accept"

    roster = client.post(
        "/decisions/roster",
        json={"league_id": "rrfl", "roster": [player("QB", "QB"), player("RB", "RB")]},
    )
    assert roster.status_code == 200
    assert roster.json()["action"] == "target"
