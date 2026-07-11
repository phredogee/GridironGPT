import pandas as pd
import streamlit as st
from gridiron_cortex.facade import CortexFacade
from apps.streamlit.components.branding import render_branding
from apps.streamlit.pages.cortex_inspector import render_cortex_inspector
from gridiron_gpt.intelligence.signal_impact_api import generate_signal_impacts
from gridiron_gpt.intelligence.momentum_engine import build_momentum_rankings
from gridiron_gpt.intelligence.player_intelligence import build_player_intelligence
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.data_ingest.player_scores import (
    build_player_scorecard,
    calculate_player_scores,
    confidence_from_signals,
    recommendation_from_score,
)
from gridiron_gpt.data_ingest.player_trends import (
    calculate_velocity,
    get_player_trend_points,
)

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
    page_title="GridironGPT",
    page_icon="🏈",
    layout="wide",
)

render_branding()


# -----------------------------
# Shared data
# -----------------------------
catalog = load_player_catalog()
player_names = sorted({item["player"] for item in catalog})

scores = apply_adjusted_scores(
    calculate_player_scores()
)

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

scorecard_repository = JsonPlayerScorecardRepository(
    "data/cortex/player_scorecards.jsonl"
)

cortex = CortexFacade()

buy_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(
        data.get("adjusted_score", data["score"])
    ) == "BUY"
]

watch_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(
        data.get("adjusted_score", data["score"])
    ) == "WATCH"
]

risk_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(
        data.get("adjusted_score", data["score"])
    ) in ["MONITOR", "SELL"]
]


# -----------------------------
# Tabs
# -----------------------------
cortex_tab, dashboard_tab, player_tab, trends_tab, momentum_tab = st.tabs(
    [
        "🧠 Cortex Inspector",
        "📊 Dashboard",
        "🏈 Player",
        "🔥 Trends",
        "🚀 Momentum",
    ]
)


# -----------------------------
# Dashboard Tab
# -----------------------------
with dashboard_tab:
    st.subheader("📊 Fantasy Signal Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("BUY candidates", len(buy_players))
        if buy_players:
            player, team = buy_players[0][0]
            score = buy_players[0][1]["score"]
            confidence = confidence_from_signals(buy_players[0][1]["signals"])
            st.write(f"Top: **{player} ({team})**")
            st.write(f"Score: `{score:+.1f}`")
            st.write(f"Confidence: `{confidence}%`")

    with col2:
        st.metric("WATCH candidates", len(watch_players))
        if watch_players:
            player, team = watch_players[0][0]
            score = watch_players[0][1]["score"]
            confidence = confidence_from_signals(watch_players[0][1]["signals"])
            st.write(f"Top: **{player} ({team})**")
            st.write(f"Score: `{score:+.1f}`")
            st.write(f"Confidence: `{confidence}%`")

    with col3:
        st.metric("Risk candidates", len(risk_players))
        if risk_players:
            player, team = risk_players[0][0]
            score = risk_players[0][1]["score"]
            confidence = confidence_from_signals(risk_players[0][1]["signals"])
            st.write(f"Top: **{player} ({team})**")
            st.write(f"Score: `{score:+.1f}`")
            st.write(f"Confidence: `{confidence}%`")
        else:
            st.write("No major risk candidates currently.")

    st.divider()

    st.subheader("🏆 Top Signal Rankings")

    if ranked_players:
        for idx, ((player, team), data) in enumerate(ranked_players[:10], start=1):
            rating = recommendation_from_score(data["score"])
            confidence = confidence_from_signals(data["signals"])

            st.write(
                f"**{idx}. {player} ({team})** — "
                f"Score: `{data['score']:+.1f}` "
                f"[{rating}; {confidence}%]"
            )
    else:
        st.info("No scored players found.")


# -----------------------------
# Player Tab
# -----------------------------
with player_tab:
    st.subheader("🏈 Player Intelligence")

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
            st.metric(
                "Recommendation",
                intel["recommendation"],
            )

        with col2:
            st.metric(
                "Score",
                f"{intel['score']:+.2f}",
            )

        with col3:
            st.metric(
                "Confidence",
                f"{intel['confidence']}%",
            )

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
# -----------------------------
# Trends Tab
# -----------------------------
with trends_tab:
    st.subheader("🔥 Momentum Tracker")

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

# -----------------------------
# Momentum Tab
# -----------------------------
with momentum_tab:
    st.subheader("🚀 Momentum Report")

    rankings = build_momentum_rankings(limit=10)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 Top Risers")

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
        st.markdown("### 🧊 Top Fallers")

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

# -----------------------------
# Cortex Inspector Tab
# -----------------------------
with cortex_tab:
    render_cortex_inspector(cortex)
