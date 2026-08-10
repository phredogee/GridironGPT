from gridiron_gpt.fantasy_decisions.models import LeagueContext, PlayerDecisionInput
from gridiron_gpt.product.commissioner_suite import (
    CommissionerInsightService,
    JsonLeagueHistoryRepository,
    LeagueSeasonArchive,
    PlayoffBracketGenerator,
    ScheduleAnalyticsService,
)
from gridiron_gpt.product.draft_room import DraftRoomService, DraftRoomState
from gridiron_gpt.product.schedule_generator import ScheduleConfig, ScheduleGenerator, ScheduleTeam
from gridiron_gpt.product.schedule_options import (
    ScheduleConstraints,
    ScheduleConstraintService,
    ScheduleOptionService,
)


def teams():
    return tuple(
        ScheduleTeam(
            team_id=f"team-{index + 1}",
            name=f"Team {index + 1}",
            division="East" if index < 5 else "West",
        )
        for index in range(10)
    )


def schedule():
    return ScheduleGenerator().generate(
        ScheduleConfig(
            teams=teams(),
            regular_season_weeks=13,
            playoff_start_week=14,
            playoff_weeks=3,
        )
    )


def player(name, position="RB", points=12):
    return PlayerDecisionInput(
        player_id=name.lower().replace(" ", "-"),
        player_name=name,
        position=position,
        team="ATL",
        cortex_score=10,
        confidence=0.8,
        projected_points=points,
        replacement_value=2,
    )


def test_schedule_analytics_scores_balanced_reference_schedule():
    result = ScheduleAnalyticsService().analyze(schedule())
    assert result.home_away_spread <= 2
    assert result.score > 0
    assert len(result.divisional_games_by_week) == 13


def test_schedule_options_preserve_matchup_count_and_rank_quality():
    original = schedule()
    options = ScheduleOptionService().generate_options(
        original,
        ScheduleConstraints(max_home_streak=3, max_away_streak=3),
        option_count=3,
    )
    assert len(options) == 3
    assert all(len(option.schedule.matchups) == len(original.matchups) for option in options)
    assert options[0].quality_score >= options[-1].quality_score or not options[0].violations


def test_rivalry_constraint_reports_missing_week():
    violations = ScheduleConstraintService().validate(
        schedule(),
        ScheduleConstraints(rivalry_week=13, rivalry_pairs=(("team-1", "team-6"),)),
    )
    assert any("rivalry" in item for item in violations)


def test_four_team_playoff_bracket_has_semifinals_and_title():
    bracket = PlayoffBracketGenerator().generate(4)
    assert bracket.rounds == 2
    assert len(bracket.matchups) == 3
    assert bracket.matchups[-1].label == "Championship"


def test_six_team_bracket_includes_top_seed_byes():
    bracket = PlayoffBracketGenerator().generate(6)
    assert bracket.rounds == 3
    assert {game.bye_seed for game in bracket.matchups if game.bye_seed} == {1, 2}


def test_unsupported_bracket_size_is_rejected():
    import pytest
    with pytest.raises(ValueError, match="4, 6, or 8"):
        PlayoffBracketGenerator().generate(5)


def test_league_history_round_trips_and_lists_seasons(tmp_path):
    repo = JsonLeagueHistoryRepository(tmp_path)
    archive = LeagueSeasonArchive(
        league_id="rrfl",
        season=2026,
        champion="Fred",
        runner_up="Sean",
        standings=({"team": "Fred", "wins": 10},),
    )
    repo.save(archive)
    assert repo.load("rrfl", 2026).champion == "Fred"
    assert repo.seasons("rrfl") == [2026]


def test_commissioner_insights_identify_points_record_and_luck():
    insights = CommissionerInsightService().summarize(
        standings=[
            {"team": "Fred", "wins": 8, "expected_wins": 6.5, "points_for": 1400},
            {"team": "Sean", "wins": 9, "expected_wins": 9.0, "points_for": 1300},
        ]
    )
    text = " ".join(insights)
    assert "Fred leads" in text
    assert "Sean currently owns" in text
    assert "outperformed" in text


def test_snake_draft_reverses_order_in_round_two():
    state = DraftRoomState(
        league=LeagueContext(teams=4),
        team_ids=("A", "B", "C", "D"),
        rounds=2,
    )
    pool = [player(f"Player {index}") for index in range(1, 9)]
    for index in range(4):
        state.draft_player(state.team_on_clock(), pool[index])
    assert state.team_on_clock() == "D"


def test_draft_room_prevents_out_of_turn_and_duplicate_picks():
    import pytest
    state = DraftRoomState(
        league=LeagueContext(teams=4),
        team_ids=("A", "B", "C", "D"),
        rounds=2,
    )
    target = player("Target")
    with pytest.raises(ValueError, match="on the clock"):
        state.draft_player("B", target)
    state.draft_player("A", target)
    with pytest.raises(ValueError, match="already been drafted"):
        state.draft_player("B", target)


def test_draft_room_recommendations_exclude_selected_players():
    state = DraftRoomState(
        league=LeagueContext(teams=4),
        team_ids=("A", "B", "C", "D"),
        rounds=2,
    )
    best = player("Best", points=20)
    state.draft_player("A", best)
    results = DraftRoomService().recommend(
        state,
        [best, player("Next", points=15), player("Other", points=10)],
    )
    assert all(item["player_name"] != "Best" for item in results)
    assert results[0]["team_on_clock"] == "B"
