from collections import Counter, defaultdict

import pytest

from gridiron_gpt.product.schedule_generator import (
    ScheduleConfig,
    ScheduleGenerator,
    ScheduleTeam,
)


def rrfl_config(regular_season_weeks=13, playoff_start_week=14, playoff_weeks=3):
    teams = tuple(
        ScheduleTeam(
            team_id=f"team-{index}",
            name=f"Team {index}",
            division="East" if index <= 5 else "West",
        )
        for index in range(1, 11)
    )
    return ScheduleConfig(
        teams=teams,
        regular_season_weeks=regular_season_weeks,
        playoff_start_week=playoff_start_week,
        playoff_weeks=playoff_weeks,
    )


def test_ten_team_two_division_schedule_has_thirteen_regular_season_weeks():
    schedule = ScheduleGenerator().generate(rrfl_config())

    assert {game.week for game in schedule.matchups} == set(range(1, 14))
    assert len(schedule.matchups) == 65
    assert schedule.playoff_weeks == (14, 15, 16)


def test_every_team_plays_once_per_regular_season_week():
    schedule = ScheduleGenerator().generate(rrfl_config())

    for week in range(1, 14):
        appearances = Counter()
        for game in schedule.matchups:
            if game.week == week:
                appearances[game.home_team_id] += 1
                appearances[game.away_team_id] += 1
        assert len(appearances) == 10
        assert set(appearances.values()) == {1}


def test_each_divisional_opponent_is_played_twice_home_and_away():
    config = rrfl_config()
    schedule = ScheduleGenerator().generate(config)
    division = {team.team_id: team.division for team in config.teams}
    pair_games = defaultdict(list)

    for game in schedule.matchups:
        pair = tuple(sorted((game.home_team_id, game.away_team_id)))
        pair_games[pair].append(game)

    for left_index, left in enumerate(config.teams):
        for right in config.teams[left_index + 1 :]:
            games = pair_games[tuple(sorted((left.team_id, right.team_id)))]
            if division[left.team_id] == division[right.team_id]:
                assert len(games) == 2
                assert {game.home_team_id for game in games} == {
                    left.team_id,
                    right.team_id,
                }


def test_each_cross_division_opponent_is_played_once():
    config = rrfl_config()
    schedule = ScheduleGenerator().generate(config)
    division = {team.team_id: team.division for team in config.teams}
    counts = Counter(
        tuple(sorted((game.home_team_id, game.away_team_id)))
        for game in schedule.matchups
    )

    for left in config.teams:
        for right in config.teams:
            if left.team_id < right.team_id and division[left.team_id] != division[right.team_id]:
                assert counts[(left.team_id, right.team_id)] == 1


def test_home_and_away_totals_are_as_even_as_mathematically_possible():
    schedule = ScheduleGenerator().generate(rrfl_config())

    for team_id in schedule.home_games:
        assert schedule.home_games[team_id] + schedule.away_games[team_id] == 13
        assert abs(schedule.home_games[team_id] - schedule.away_games[team_id]) == 1


def test_schedule_generation_is_deterministic():
    generator = ScheduleGenerator()

    first = generator.generate(rrfl_config())
    second = generator.generate(rrfl_config())

    assert first.matchups == second.matchups
    assert first.home_games == second.home_games


def test_regular_season_cannot_be_shorter_than_required_matchups():
    with pytest.raises(ValueError, match="at least 13 weeks"):
        rrfl_config(regular_season_weeks=12, playoff_start_week=13)


def test_playoffs_must_start_immediately_after_regular_season():
    with pytest.raises(ValueError, match="immediately follow"):
        rrfl_config(playoff_start_week=15)


def test_divisions_must_be_evenly_sized():
    teams = tuple(
        ScheduleTeam(
            team_id=f"team-{index}",
            name=f"Team {index}",
            division="East" if index <= 6 else "West",
        )
        for index in range(1, 11)
    )

    with pytest.raises(ValueError, match="same number"):
        ScheduleConfig(
            teams=teams,
            regular_season_weeks=14,
            playoff_start_week=15,
            playoff_weeks=2,
        )
