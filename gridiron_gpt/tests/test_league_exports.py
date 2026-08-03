from datetime import datetime, timezone

import pytest

from gridiron_gpt.product.league_exports import LeagueExportService
from gridiron_gpt.product.schedule_generator import ScheduleConfig, ScheduleGenerator, ScheduleTeam


def schedule():
    teams = tuple(
        ScheduleTeam(
            team_id=f"team-{index + 1}",
            name=f"Team {index + 1}",
            division="East" if index < 2 else "West",
        )
        for index in range(4)
    )
    return ScheduleGenerator().generate(
        ScheduleConfig(
            teams=teams,
            regular_season_weeks=4,
            playoff_start_week=5,
            playoff_weeks=2,
        )
    )


def test_schedule_csv_contains_named_matchups():
    generated = schedule()
    names = {team.team_id: team.name for team in generated.config.teams}
    output = LeagueExportService().schedule_csv(generated, names)
    assert "Away Team,Home Team" in output
    assert "Team 1" in output


def test_schedule_ical_contains_one_event_per_matchup():
    generated = schedule()
    names = {team.team_id: team.name for team in generated.config.teams}
    output = LeagueExportService().schedule_ical(
        generated,
        names,
        season_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )
    assert output.startswith("BEGIN:VCALENDAR")
    assert output.count("BEGIN:VEVENT") == len(generated.matchups)
    assert "SUMMARY:" in output


def test_schedule_ical_requires_timezone_aware_start():
    generated = schedule()
    names = {team.team_id: team.name for team in generated.config.teams}
    with pytest.raises(ValueError, match="timezone-aware"):
        LeagueExportService().schedule_ical(
            generated,
            names,
            season_start=datetime(2026, 9, 1),
        )
