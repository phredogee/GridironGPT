import streamlit as st
from apps.streamlit.components.theme import apply_cortex_theme
from apps.streamlit.pages.dashboard import render_dashboard
from apps.streamlit.pages.ingestion_status import render_ingestion_status
from gridiron_cortex.presentation.builders.dashboard_builder import (
    build_dashboard_view_model,
)
from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.advisor.roster_advisor import RosterAdvisor
from apps.streamlit.pages.cortex_inspector import render_cortex_inspector
from gridiron_gpt.intelligence.signal_impact_api import generate_signal_impacts
from gridiron_gpt.intelligence.momentum_engine import build_momentum_rankings
from gridiron_gpt.intelligence.player_intelligence import build_player_intelligence
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
    recommendation_from_score,
)
from gridiron_gpt.data_ingest.player_trends import calculate_velocity
from apps.streamlit.components.app_shell import (
    NAVIGATION_ITEMS,
    render_shell_header,
    render_sidebar,
)
from apps.streamlit.components.branding import get_project_version


def apply_adjusted_scores(scores_dict):
    adjusted = {}

    for (player, team), data in scores_dict.items():
        score = data["score"]
        impact_report = generate_signal_impacts(player, score)

        updated_data = dict(data)
        updated_data["base_score"] = score
        updated_data["adjusted_score"] = impact_report["total_system_impact"]
        updated_data["propagated_impacts"] = impact_report["propagated_impacts"]
        adjusted[(player, team)] = updated_data

    return adjusted


st.set_page_config(
    page_title="GridironGPT | Cortex Engine",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_cortex_theme()

# Shared data
catalog = load_player_catalog()
player_names = sorted({item["player"] for item in catalog})

scores = apply_adjusted_scores(calculate_player_scores())

ranked_players = sorted(
    scores.items(),
    key=lambda item: item[1].get("adjusted_score", item[1]["score"]),
    reverse=True,
)
ranked_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if data["score"] != 0
]

roster_advisor = RosterAdvisor(
    ranked_players=ranked_players,
    recommendation_from_score=recommendation_from_score,
    confidence_from_signals=confidence_from_signals,
)

cortex = CortexFacade()

buy_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data.get("adjusted_score", data["score"])) == "BUY"
]
watch_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data.get("adjusted_score", data["score"])) == "WATCH"
]
risk_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data.get("adjusted_score", data["score"]))
    in ["MONITOR", "SELL"]
]

# Navigation
version = get_project_version()
selected_page = render_sidebar(version=version)
page_metadata = NAVIGATION_ITEMS[selected_page]

render_shell_header(
    page_name=page_metadata["label"],
    description=page_metadata["description"],
)
st.divider()

if selected_page == "Inspector":
    render_cortex_inspector(cortex)

if selected_page == "Ingestion":
    render_ingestion_status()

if selected_page == "Dashboard":
    dashboard = build_dashboard_view_model(
        ranked_players=ranked_players,
        buy_players=buy_players,
        watch_players=watch_players,
        risk_players=risk_players,
        player_count=len(player_names),
        recommendation_from_score=recommendation_from_score,
        confidence_from_signals=confidence_from_signals,
        passing_tests=43,
    )
    render_dashboard(dashboard)

if selected_page == "Advisor":
    st.markdown("### Ask Cortex")
    st.caption("Ask football questions in natural language.")

    question = st.text_area(
        "Ask Gridiron Cortex",
        placeholder=(
            "Examples:\n"
            "• Who should I start this week?\n"
            "• Best waiver pickup over the next 3 weeks?\n"
            "• Should I trade Tank Dell?\n"
            "• Best DST to stream next week?"
        ),
        height=140,
    )

    if st.button("Ask Cortex", use_container_width=True):
        if question.strip():
            response = roster_advisor.answer(question)
            st.markdown("### Cortex Response")
            st.write(response["answer"])
            st.metric("Confidence", f"{response['confidence']}%")

            if response["details"]:
                with st.expander("Reasoning", expanded=True):
                    for detail in response["details"]:
                        st.write(f"• {detail}")

            st.markdown("### Your Question")
            st.write(question)
            st.markdown("### Planned Cortex Workflow")

            workflow = [
                "Interpret question",
                "Identify players/teams",
                "Search scorecards",
                "Expand knowledge graph",
                "Evaluate propagation",
                "Generate recommendation",
                "Explain reasoning",
            ]
            for step in workflow:
                st.write(f"• {step}")
        else:
            st.warning("Enter a question first.")

if selected_page == "Players":
    st.markdown("### Player Intelligence")

    default_player = "Tank Dell" if "Tank Dell" in player_names else player_names[0]
    selected_player = st.selectbox(
        "Select player",
        player_names,
        index=player_names.index(default_player),
    )

    intel = build_player_intelligence(selected_player)

    if intel["status"] == "not_found":
        st.warning(f"No intelligence found for {selected_player}.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Recommendation", intel["recommendation"])
        with col2:
            st.metric("Score", f"{intel['score']:+.2f}")
        with col3:
            st.metric("Confidence", f"{intel['confidence']}%")

        st.divider()
        st.markdown("### 🚀 Momentum")
        momentum = intel["momentum"]

        if momentum.get("status") == "first_snapshot":
            st.info("First snapshot recorded. More history is needed for momentum.")
        elif momentum.get("status") == "ok":
            st.metric(
                "Momentum Score",
                f"{momentum.get('momentum_score', 0):+.2f}",
                delta=momentum.get("direction", "stable"),
            )
            st.write(f"Direction: **{momentum.get('direction', 'stable').upper()}**")
        else:
            st.info("No momentum history available yet.")

        st.divider()
        st.markdown("### 📈 Trend")
        trend = intel["trend"]

        if trend.get("status") == "first_snapshot":
            st.info("First trend snapshot recorded. More history is needed.")
        elif trend.get("status") == "ok":
            st.write(f"Current Score: `{trend.get('current_score')}`")
            st.write(f"Previous Score: `{trend.get('previous_score')}`")
            st.write(f"Change: `{trend.get('change'):+.2f}`")
            st.write(f"Direction: **{trend.get('direction', 'stable').upper()}**")
        else:
            st.info("No trend history available yet.")

        st.divider()
        st.markdown("### 📰 Recent Signals")
        recent_signals = intel.get("recent_signals", [])

        if recent_signals:
            for signal in recent_signals:
                st.write(
                    f"- **[{signal.get('source')}]** "
                    f"`{signal.get('impact')}` "
                    f"`{signal.get('value'):+.2f}` — "
                    f"{signal.get('headline')}"
                )
        else:
            st.info("No recent signals found.")

if selected_page == "Trends":
    st.markdown("### Trending Players")

    hot_players = []
    cold_players = []

    for (player, team), data in scores.items():
        velocity = calculate_velocity(player)
        confidence = confidence_from_signals(data["signals"])

        item = {
            "player": player,
            "team": team,
            "velocity": velocity["velocity"],
            "direction": velocity["direction"],
            "confidence": confidence,
            "score": data["score"],
        }

        if velocity["velocity"] > 0:
            hot_players.append(item)
        if velocity["velocity"] < 0:
            cold_players.append(item)

    hot_players.sort(key=lambda item: item["velocity"], reverse=True)
    cold_players.sort(key=lambda item: item["velocity"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔥 Hot Players")
        if hot_players:
            for item in hot_players[:5]:
                st.metric(
                    label=f"{item['player']} ({item['team']})",
                    value=f"{item['velocity']:+.2f}/week",
                    delta=f"{item['confidence']}% confidence",
                )
        else:
            st.info("No hot players found.")

    with col2:
        st.markdown("### 🧊 Cold Players")
        if cold_players:
            for item in cold_players[:5]:
                st.metric(
                    label=f"{item['player']} ({item['team']})",
                    value=f"{item['velocity']:+.2f}/week",
                    delta=f"{item['confidence']}% confidence",
                )
        else:
            st.info("No cooling players found.")

if selected_page == "Trajectory":
    st.subheader("🚀 Trajectory")
    rankings = build_momentum_rankings(limit=10)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Risers")
        if rankings["risers"]:
            for item in rankings["risers"]:
                st.metric(
                    label=f"{item['player']} ({item.get('team') or 'UNK'})",
                    value=f"{item['current_score']:+.2f}",
                    delta=f"{item['change']:+.2f}",
                )
                st.caption(f"Velocity: {item['velocity']:+.2f}")
        else:
            st.info("No risers yet. More score snapshots are needed.")

    with col2:
        st.markdown("### Top Fallers")
        if rankings["fallers"]:
            for item in rankings["fallers"]:
                st.metric(
                    label=f"{item['player']} ({item.get('team') or 'UNK'})",
                    value=f"{item['current_score']:+.2f}",
                    delta=f"{item['change']:+.2f}",
                )
                st.caption(f"Velocity: {item['velocity']:+.2f}")
        else:
            st.info("No fallers yet. More score snapshots are needed.")

    st.divider()
    st.markdown("### 🆕 First Snapshots")

    if rankings["first_snapshots"]:
        for item in rankings["first_snapshots"]:
            st.write(
                f"- **{item['player']} ({item.get('team') or 'UNK'})** — "
                f"Current Score: `{float(item.get('current_score') or 0):+.2f}`"
            )
    else:
        st.info("No first snapshots found.")
