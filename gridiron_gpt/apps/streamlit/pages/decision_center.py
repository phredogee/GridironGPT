from __future__ import annotations

from pathlib import Path

import streamlit as st

from gridiron_gpt.fantasy_decisions.decision_engine import FantasyDecisionEngine
from gridiron_gpt.fantasy_decisions.models import PlayerDecisionInput, TradeSide
from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository


def render_decision_center(
    players: list[PlayerDecisionInput],
    data_directory: str | Path = "data/leagues",
) -> None:
    repository = JsonLeagueProfileRepository(data_directory)
    profiles = repository.list()
    engine = FantasyDecisionEngine()

    st.markdown("### Fantasy Decision Center")
    st.caption("Turn Cortex scores into league-aware draft, lineup, waiver, trade, and roster decisions.")

    if not profiles:
        st.warning("Create a league profile in League Settings before using league-aware decisions.")
        return

    profile = repository.load(st.selectbox("League", [item.league_id for item in profiles]))
    league = profile.to_context()
    names = [player.player_name for player in players]
    by_name = {player.player_name: player for player in players}

    tabs = st.tabs(["Draft", "Start / Sit", "Waivers", "Trade", "Roster"])

    with tabs[0]:
        ranked = engine.rank_draft(players, league)
        st.dataframe(
            [
                {
                    "Rank": item.metadata.get("rank"),
                    "Player": item.player_name,
                    "Action": item.action.value,
                    "Score": item.score,
                    "Confidence": item.confidence,
                    "Why": "; ".join(item.reasons),
                }
                for item in ranked[:50]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:
        selected = st.multiselect("Lineup candidates", names, key="start_sit_candidates")
        slots = st.number_input("Starting slots", min_value=1, max_value=20, value=1)
        if st.button("Build lineup") and selected:
            decisions = engine.start_sit([by_name[name] for name in selected], slots=int(slots))
            for decision in decisions:
                st.write(f"**{decision.action.value.upper()} — {decision.player_name}** · {decision.score:.2f}")
                st.caption("; ".join(decision.reasons))

    with tabs[2]:
        roster_names = st.multiselect("Current roster", names, key="waiver_roster")
        free_agent_names = st.multiselect("Available players", names, key="waiver_free_agents")
        if st.button("Rank waiver options") and free_agent_names:
            decisions = engine.waiver_recommendations(
                [by_name[name] for name in free_agent_names],
                league,
                [by_name[name] for name in roster_names],
            )
            for decision in decisions:
                st.write(
                    f"**{decision.action.value.upper()} — {decision.player_name}** · "
                    f"FAAB ${decision.metadata.get('faab_bid', 0)}"
                )
                st.caption("; ".join(decision.reasons))

    with tabs[3]:
        give = st.multiselect("Players you give", names, key="trade_give")
        receive = st.multiselect("Players you receive", names, key="trade_receive")
        if st.button("Evaluate trade") and give and receive:
            decision = engine.evaluate_trade(
                TradeSide(tuple(by_name[name] for name in give)),
                TradeSide(tuple(by_name[name] for name in receive)),
            )
            st.metric("Recommendation", decision.action.value.upper(), delta=f"Value {decision.score:+.2f}")
            st.write(decision.summary)
            for reason in decision.reasons:
                st.write(f"- {reason}")

    with tabs[4]:
        roster = st.multiselect("Analyze roster", names, key="roster_analysis")
        if st.button("Analyze roster construction") and roster:
            decision = engine.roster_analysis([by_name[name] for name in roster], league)
            st.metric("Roster action", decision.action.value.upper())
            st.write(decision.summary)
            st.json(decision.metadata)
