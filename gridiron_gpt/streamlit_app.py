import pandas as pd
import streamlit as st

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


st.set_page_config(
    page_title="GridironGPT",
    page_icon="🏈",
    layout="wide",
)

st.title("🏈 GridironGPT")
st.caption("Fantasy Football Intelligence Platform")


# -----------------------------
# Shared data
# -----------------------------
catalog = load_player_catalog()
player_names = sorted({item["player"] for item in catalog})

scores = calculate_player_scores()

ranked_players = sorted(
    scores.items(),
    key=lambda item: item[1]["score"],
    reverse=True,
)

ranked_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if data["score"] != 0
]

buy_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data["score"]) == "BUY"
]

watch_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data["score"]) == "WATCH"
]

risk_players = [
    ((player, team), data)
    for (player, team), data in ranked_players
    if recommendation_from_score(data["score"]) in ["MONITOR", "SELL"]
]


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "📊 Dashboard",
        "🏈 Player",
        "🔥 Trends",
    ]
)


# -----------------------------
# Dashboard Tab
# -----------------------------
with tab1:
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
with tab2:
    st.subheader("🏈 Player Intelligence")

    default_player = "Tank Dell" if "Tank Dell" in player_names else player_names[0]

    selected_player = st.selectbox(
        "Select player",
        player_names,
        index=player_names.index(default_player),
    )

    trend_points = get_player_trend_points(selected_player)

    st.markdown(f"### {selected_player} Trend")

    if trend_points:
        df = pd.DataFrame(trend_points)
        df["date"] = pd.to_datetime(df["date"])

        st.line_chart(
            df,
            x="date",
            y="cumulative_score",
        )

        st.markdown("### Scorecard")
        st.text(build_player_scorecard(selected_player))
    else:
        st.info(f"No trend data found for {selected_player}.")


# -----------------------------
# Trends Tab
# -----------------------------
with tab3:
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
