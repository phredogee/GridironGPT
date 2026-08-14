from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader


def test_parses_average_draft_position_from_player_ownership():
    payload = {
        "players": [
            {
                "player": {
                    "fullName": "Jahmyr Gibbs",
                    "ownership": {"averageDraftPosition": 2.7},
                }
            },
            {
                "player": {
                    "fullName": "Bijan Robinson",
                    "ownership": {"averageDraftPosition": 4.1},
                }
            },
        ]
    }

    snapshot = EspnAdpLoader(json_loader=lambda: payload).load()

    assert snapshot.source == "ESPN"
    assert snapshot.records == {
        "Jahmyr Gibbs": 2.7,
        "Bijan Robinson": 4.1,
    }


def test_supports_flat_player_entries_and_skips_missing_or_invalid_adp():
    payload = {
        "players": [
            {
                "fullName": "Puka Nacua",
                "ownership": {"averageDraftPosition": "3.5"},
            },
            {
                "fullName": "No ADP Player",
                "ownership": {},
            },
            {
                "fullName": "Bad ADP Player",
                "ownership": {"averageDraftPosition": 0},
            },
        ]
    }

    snapshot = EspnAdpLoader(json_loader=lambda: payload).load()

    assert snapshot.records == {"Puka Nacua": 3.5}


def test_non_player_payload_returns_empty_snapshot():
    snapshot = EspnAdpLoader(json_loader=lambda: {"status": "ok"}).load()
    assert snapshot.records == {}
