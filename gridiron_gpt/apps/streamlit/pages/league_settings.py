from __future__ import annotations

from pathlib import Path

import streamlit as st

from gridiron_gpt.fantasy_decisions.models import ScoringFormat
from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository, LeagueProfile


POSITIONS = ("QB", "RB", "WR", "TE", "FLEX", "SUPERFLEX", "DST", "K")


def render_league_settings(data_directory: str | Path = "data/leagues") -> None:
    repository = JsonLeagueProfileRepository(data_directory)
    profiles = repository.list()

    st.markdown("### League Profiles")
    st.caption("Create or edit league size, roster limits, lineup slots, scoring, and FAAB rules.")

    profile_ids = [profile.league_id for profile in profiles]
    selected_id = st.selectbox("Existing profile", ["New league", *profile_ids])
    current = repository.load(selected_id) if selected_id != "New league" else None

    with st.form("league_profile_form"):
        league_id = st.text_input("League ID", value=current.league_id if current else "")
        name = st.text_input("League name", value=current.name if current else "")
        col1, col2, col3 = st.columns(3)
        teams = col1.number_input("Teams", min_value=2, max_value=32, value=current.teams if current else 12)
        roster_size = col2.number_input("Roster size", min_value=1, max_value=40, value=current.roster_size if current else 16)
        faab_budget = col3.number_input("FAAB budget", min_value=0, max_value=1000, value=current.faab_budget if current else 100)

        col4, col5, col6 = st.columns(3)
        bench_slots = col4.number_input("Bench slots", min_value=0, max_value=30, value=current.bench_slots if current else 6)
        ir_slots = col5.number_input("IR slots", min_value=0, max_value=10, value=current.ir_slots if current else 1)
        scoring = col6.selectbox(
            "Scoring format",
            [item.value for item in ScoringFormat],
            index=[item.value for item in ScoringFormat].index(
                current.scoring_format.value if current else ScoringFormat.HALF_PPR.value
            ),
        )

        st.markdown("#### Starting lineup")
        slot_columns = st.columns(4)
        starting_slots = {}
        for index, position in enumerate(POSITIONS):
            default = (current.starting_slots.get(position, 0) if current else {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}.get(position, 0))
            starting_slots[position] = slot_columns[index % 4].number_input(
                position, min_value=0, max_value=8, value=default, key=f"slot_{position}"
            )

        submitted = st.form_submit_button("Save league profile", use_container_width=True)

    if submitted:
        try:
            profile = LeagueProfile(
                league_id=league_id.strip(),
                name=name.strip(),
                teams=int(teams),
                roster_size=int(roster_size),
                starting_slots={key: int(value) for key, value in starting_slots.items() if value > 0},
                bench_slots=int(bench_slots),
                ir_slots=int(ir_slots),
                faab_budget=int(faab_budget),
                scoring_format=ScoringFormat(scoring),
            )
            repository.save(profile)
            st.success(f"Saved {profile.name}.")
        except ValueError as exc:
            st.error(str(exc))

    if current and st.button("Delete selected profile"):
        repository.delete(current.league_id)
        st.success(f"Deleted {current.name}.")
