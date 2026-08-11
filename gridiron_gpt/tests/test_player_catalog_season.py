from gridiron_gpt.data_ingest import player_catalog


class FakeRoster:
    def __init__(self, rows):
        self.rows = rows

    def iter_rows(self, *, named=False):
        assert named is True
        return iter(self.rows)


def _row(**overrides):
    row = {
        "gsis_id": "00-1234567",
        "full_name": "Test Player",
        "football_name": "Test",
        "first_name": "Test",
        "last_name": "Player",
        "team": "HOU",
        "position": "WR",
        "depth_chart_position": "WR",
        "status": "ACT",
        "status_description_abbr": "A01",
        "week": 0,
        "game_type": "PRE",
    }
    row.update(overrides)
    return row


def test_build_player_catalog_uses_roster_aware_current_season(monkeypatch, tmp_path):
    requested = {}

    def fake_current_season(*, roster=False):
        assert roster is True
        return 2026

    def fake_load_rosters(seasons):
        requested["seasons"] = seasons
        return FakeRoster([_row()])

    monkeypatch.setattr(player_catalog.nfl, "get_current_season", fake_current_season)
    monkeypatch.setattr(player_catalog.nfl, "load_rosters", fake_load_rosters)

    catalog = player_catalog.build_player_catalog(tmp_path / "players.json")

    assert requested["seasons"] == [2026]
    assert catalog[0]["status_description_abbr"] == "A01"
    assert catalog[0]["week"] == 0
    assert catalog[0]["game_type"] == "PRE"


def test_build_player_catalog_accepts_explicit_season(monkeypatch, tmp_path):
    requested = {}

    def fake_load_rosters(seasons):
        requested["seasons"] = seasons
        return FakeRoster([_row()])

    monkeypatch.setattr(player_catalog.nfl, "load_rosters", fake_load_rosters)

    player_catalog.build_player_catalog(
        tmp_path / "players.json",
        season=2025,
    )

    assert requested["seasons"] == [2025]
