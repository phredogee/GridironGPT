import sys
from types import SimpleNamespace

import pandas as pd

from gridiron_gpt.draft.bye_week_service import ByeWeekService


def test_bye_week_service_derives_single_missing_regular_season_week(monkeypatch):
    frame = pd.DataFrame(
        [
            {
                "week": week,
                "home_team": "BUF",
                "away_team": "MIA",
                "game_type": "REG",
            }
            for week in range(1, 19)
            if week != 7
        ]
    )
    fake = SimpleNamespace(load_schedules=lambda seasons: frame)
    monkeypatch.setitem(sys.modules, "nflreadpy", fake)

    result = ByeWeekService().load(season=2026)

    assert result["BUF"] == 7
    assert result["MIA"] == 7


def test_bye_week_service_does_not_guess_from_partial_schedule(monkeypatch):
    frame = pd.DataFrame(
        [
            {
                "week": week,
                "home_team": "BUF",
                "away_team": "MIA",
                "game_type": "REG",
            }
            for week in range(1, 6)
        ]
    )
    fake = SimpleNamespace(load_schedules=lambda seasons: frame)
    monkeypatch.setitem(sys.modules, "nflreadpy", fake)

    assert ByeWeekService().load(season=2026) == {}
