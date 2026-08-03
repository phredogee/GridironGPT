from __future__ import annotations

import csv
import io

import streamlit as st

from gridiron_gpt.product.schedule_generator import (
    ScheduleConfig,
    ScheduleGenerator,
    ScheduleTeam,
)


def _team_rows(team_count: int, division_count: int) -> list[ScheduleTeam]:
    teams_per_division = team_count // division_count
    divisions = [f"Division {index + 1}" for index in range(division_count)]
    teams: list[ScheduleTeam] = []
    for index in range(team_count):
        division = divisions[index // teams_per_division]
        name = st.text_input(
            f"Team {index + 1}",
            value=f"Team {index + 1}",
            key=f"schedule_team_{index}",
        )
        teams.append(
            ScheduleTeam(
                team_id=f"team-{index + 1}",
                name=name.strip() or f"Team {index + 1}",
                division=division,
            )
        )
    return teams


def _csv(schedule, name_by_id: dict[str, str]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Week", "Away Team", "Home Team", "Divisional"])
    for game in schedule.matchups:
        writer.writerow(
            [
                game.week,
                name_by_id[game.away_team_id],
                name_by_id[game.home_team_id],
                "Yes" if game.divisional else "No",
            ]
        )
    return output.getvalue()


def render_schedule_generator() -> None:
    st.markdown("### League Schedule Generator")
    st.caption(
        "Guarantees two divisional meetings per opponent—one home and one away—"
        "then schedules every non-divisional opponent once and balances home/away totals."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        team_count = st.number_input("Teams", min_value=4, max_value=20, value=10, step=2)
    with col2:
        division_count = st.number_input("Divisions", min_value=2, max_value=5, value=2, step=1)
    with col3:
        regular_weeks = st.number_input("Regular-season weeks", min_value=1, max_value=20, value=13)
    with col4:
        playoff_weeks = st.number_input("Playoff weeks", min_value=1, max_value=6, value=3)

    playoff_start = int(regular_weeks) + 1
    st.info(
        f"Playoffs will begin in Week {playoff_start} and run through "
        f"Week {playoff_start + int(playoff_weeks) - 1}."
    )

    if int(team_count) % int(division_count) != 0:
        st.error("Teams must divide evenly across divisions.")
        return

    with st.expander("Team names", expanded=False):
        teams = _team_rows(int(team_count), int(division_count))

    if st.button("Generate Schedule", use_container_width=True):
        try:
            config = ScheduleConfig(
                teams=tuple(teams),
                regular_season_weeks=int(regular_weeks),
                playoff_start_week=playoff_start,
                playoff_weeks=int(playoff_weeks),
            )
            schedule = ScheduleGenerator().generate(config)
        except ValueError as exc:
            st.error(str(exc))
            return

        name_by_id = {team.team_id: team.name for team in teams}
        st.session_state.generated_schedule = schedule
        st.session_state.generated_schedule_names = name_by_id

    schedule = st.session_state.get("generated_schedule")
    name_by_id = st.session_state.get("generated_schedule_names", {})
    if schedule is None:
        return

    st.success(
        f"Generated {len(schedule.matchups)} regular-season games across "
        f"{schedule.config.regular_season_weeks} weeks."
    )

    for week in range(1, schedule.config.regular_season_weeks + 1):
        with st.expander(f"Week {week}", expanded=week == 1):
            rows = []
            for game in schedule.matchups:
                if game.week == week:
                    rows.append(
                        {
                            "Away": name_by_id[game.away_team_id],
                            "Home": name_by_id[game.home_team_id],
                            "Divisional": "Yes" if game.divisional else "No",
                        }
                    )
            st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### Home/Away Balance")
    balance_rows = [
        {
            "Team": name_by_id[team_id],
            "Home": schedule.home_games[team_id],
            "Away": schedule.away_games[team_id],
            "Difference": schedule.home_games[team_id] - schedule.away_games[team_id],
        }
        for team_id in sorted(schedule.home_games)
    ]
    st.dataframe(balance_rows, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Schedule CSV",
        data=_csv(schedule, name_by_id),
        file_name="fantasy_schedule.csv",
        mime="text/csv",
        use_container_width=True,
    )
