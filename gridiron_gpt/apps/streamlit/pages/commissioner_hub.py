from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from gridiron_gpt.fantasy_decisions.models import LeagueContext, PlayerDecisionInput
from gridiron_gpt.product.commissioner_suite import (
    CommissionerInsightService,
    JsonLeagueHistoryRepository,
    LeagueSeasonArchive,
    PlayoffBracketGenerator,
    ScheduleAnalyticsService,
)
from gridiron_gpt.product.draft_room import DraftRoomService, DraftRoomState
from gridiron_gpt.product.schedule_options import ScheduleConstraints, ScheduleOptionService


_HISTORY = JsonLeagueHistoryRepository(Path("data/league_history"))


def render_commissioner_hub(players: list[PlayerDecisionInput]) -> None:
    st.markdown("### Commissioner Hub")
    st.caption("Schedule analysis, playoff planning, league history, commissioner insights, and live draft support.")
    tabs = st.tabs(["Schedule Lab", "Playoffs", "League History", "Insights", "Draft Room"])

    with tabs[0]:
        _schedule_lab()
    with tabs[1]:
        _playoffs()
    with tabs[2]:
        _history()
    with tabs[3]:
        _insights()
    with tabs[4]:
        _draft_room(players)


def _schedule_lab() -> None:
    schedule = st.session_state.get("generated_schedule")
    if schedule is None:
        st.info("Generate a schedule in Schedule Generator first.")
        return
    analytics = ScheduleAnalyticsService().analyze(schedule)
    col1, col2, col3 = st.columns(3)
    col1.metric("Schedule quality", f"{analytics.score:.1f}/100")
    col2.metric("Home/away spread", analytics.home_away_spread)
    col3.metric("Maximum repeat count", max(analytics.repeat_opponents.values(), default=0))
    st.dataframe(
        [
            {
                "Team": team_id,
                "Longest home streak": analytics.longest_home_streak[team_id],
                "Longest away streak": analytics.longest_away_streak[team_id],
                "Repeat opponents": analytics.repeat_opponents[team_id],
            }
            for team_id in analytics.longest_home_streak
        ],
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("#### Generate alternatives")
    c1, c2, c3 = st.columns(3)
    max_home = c1.number_input("Maximum home streak", 1, 6, 3)
    max_away = c2.number_input("Maximum away streak", 1, 6, 3)
    option_count = c3.number_input("Schedule options", 1, 8, 3)
    if st.button("Rank Schedule Options", use_container_width=True):
        options = ScheduleOptionService().generate_options(
            schedule,
            ScheduleConstraints(max_home_streak=int(max_home), max_away_streak=int(max_away)),
            option_count=int(option_count),
        )
        st.session_state.schedule_options = options
    for option in st.session_state.get("schedule_options", []):
        with st.expander(f"Option {option.option_number} — score {option.quality_score:.1f}"):
            if option.violations:
                for violation in option.violations:
                    st.warning(violation)
            else:
                st.success("No configured constraint violations.")


def _playoffs() -> None:
    playoff_teams = st.selectbox("Playoff teams", [4, 6, 8], index=1)
    bracket = PlayoffBracketGenerator().generate(int(playoff_teams))
    st.metric("Rounds", bracket.rounds)
    st.dataframe(
        [
            {
                "Round": game.round_number,
                "Matchup": game.label,
                "Seed A": game.seed_a or "TBD",
                "Seed B": game.seed_b or "TBD",
                "Bye seed": game.bye_seed or "",
            }
            for game in bracket.matchups
        ],
        hide_index=True,
        use_container_width=True,
    )


def _history() -> None:
    league_id = st.text_input("League ID", value="rrfl", key="history_league")
    season = st.number_input("Season", 2000, 2100, 2026, key="history_season")
    champion = st.text_input("Champion", key="history_champion")
    runner_up = st.text_input("Runner-up", key="history_runner_up")
    standings_json = st.text_area(
        "Standings JSON",
        value='[{"team":"Team 1","wins":10,"losses":3,"points_for":1500}]',
        height=120,
    )
    if st.button("Archive Season", use_container_width=True):
        try:
            standings = tuple(json.loads(standings_json))
            archive = LeagueSeasonArchive(
                league_id=league_id,
                season=int(season),
                champion=champion or None,
                runner_up=runner_up or None,
                standings=standings,
            )
            _HISTORY.save(archive)
            st.success(f"Archived {league_id} {season}.")
        except (ValueError, json.JSONDecodeError) as exc:
            st.error(str(exc))
    seasons = _HISTORY.seasons(league_id) if league_id else []
    if seasons:
        selected = st.selectbox("Archived season", seasons)
        archive = _HISTORY.load(league_id, int(selected))
        st.write(f"Champion: **{archive.champion or 'Unknown'}**")
        st.write(f"Runner-up: **{archive.runner_up or 'Unknown'}**")
        st.dataframe(list(archive.standings), hide_index=True, use_container_width=True)


def _insights() -> None:
    standings_json = st.text_area(
        "Standings and expected-win data",
        value=(
            '[{"team":"Fred","wins":8,"expected_wins":6.5,"points_for":1400},'
            '{"team":"Sean","wins":9,"expected_wins":9.0,"points_for":1300}]'
        ),
        height=150,
        key="insight_standings",
    )
    if st.button("Generate Commissioner Insights", use_container_width=True):
        try:
            insights = CommissionerInsightService().summarize(standings=json.loads(standings_json))
            for insight in insights:
                st.info(insight)
        except json.JSONDecodeError as exc:
            st.error(str(exc))


def _draft_room(players: list[PlayerDecisionInput]) -> None:
    team_count = st.number_input("Draft teams", 4, 20, 10, step=2)
    rounds = st.number_input("Draft rounds", 1, 30, 15)
    team_ids = tuple(f"Team {index + 1}" for index in range(int(team_count)))
    state_key = f"draft_state_{team_count}_{rounds}"
    if state_key not in st.session_state:
        st.session_state[state_key] = DraftRoomState(
            league=LeagueContext(teams=int(team_count)),
            team_ids=team_ids,
            rounds=int(rounds),
        )
    state: DraftRoomState = st.session_state[state_key]
    on_clock = state.team_on_clock()
    st.metric("On the clock", on_clock or "Draft complete")
    recommendations = DraftRoomService().recommend(state, players, limit=10)
    if recommendations:
        st.dataframe(recommendations, hide_index=True, use_container_width=True)
        available_names = [item["player_name"] for item in recommendations]
        selected_name = st.selectbox("Draft player", available_names)
        selected = next(player for player in players if player.player_name == selected_name)
        if st.button("Record Pick", use_container_width=True):
            try:
                state.draft_player(on_clock, selected)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    if state.picks:
        st.markdown("#### Draft board")
        st.dataframe(
            [
                {
                    "Overall": pick.overall_pick,
                    "Round": pick.round_number,
                    "Pick": pick.pick_in_round,
                    "Fantasy team": pick.fantasy_team_id,
                    "Player": pick.player_name,
                    "Position": pick.position,
                }
                for pick in state.picks
            ],
            hide_index=True,
            use_container_width=True,
        )
