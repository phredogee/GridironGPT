import streamlit as st
from apps.streamlit.components.theme import apply_cortex_theme
from apps.streamlit.pages.dashboard import render_dashboard
from apps.streamlit.pages.ingestion_status import render_ingestion_status
from apps.streamlit.pages.cortex_explorer import render_cortex_explorer
from apps.streamlit.components.intelligence_charts import render_confidence_panel, render_cortex_timeline, render_signal_breakdown
from gridiron_cortex.presentation.builders.dashboard_builder import build_dashboard_view_model
from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.activity.activity_feed_service import ActivityFeedService
from gridiron_cortex.advisor.roster_advisor import RosterAdvisor
from apps.streamlit.pages.cortex_inspector import render_cortex_inspector
from gridiron_gpt.intelligence.signal_impact_api import generate_signal_impacts
from gridiron_gpt.intelligence.momentum_engine import build_momentum_rankings
from gridiron_gpt.intelligence.player_intelligence import build_player_intelligence
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.data_ingest.player_scores import calculate_player_scores, confidence_from_signals, recommendation_from_score
from gridiron_gpt.data_ingest.player_trends import calculate_velocity
from apps.streamlit.components.app_shell import NAVIGATION_ITEMS, render_shell_header, render_sidebar
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


def _advisor_match(question: str, ranked):
    normalized = question.lower()
    for (player, team), data in ranked:
        if player.lower() in normalized:
            return player, team, data
    return None


def _render_intelligence_bars(data: dict) -> None:
    signals = data.get("signals", [])
    positive = sum(max(float(signal.get("value", 0.0)), 0.0) for signal in signals)
    negative = sum(abs(min(float(signal.get("value", 0.0)), 0.0)) for signal in signals)
    total = positive + negative
    opportunity = min(100, int(50 + positive * 25))
    momentum = min(100, int(50 + max(float(data.get("adjusted_score", data.get("score", 0.0))), 0.0) * 20))
    risk = min(100, int((negative / total) * 100)) if total else 0
    health = max(0, 100 - risk)
    upside = min(100, int((opportunity + momentum) / 2))
    st.markdown("### Cortex Profile")
    for label, value in (("Health", health), ("Opportunity", opportunity), ("Momentum", momentum), ("Risk", risk), ("Upside", upside)):
        left, right = st.columns([4, 1])
        with left:
            st.caption(label); st.progress(value / 100)
        with right:
            st.metric(label="", value=f"{value}%")


def _render_advisor_result(question: str, response: dict, ranked) -> None:
    matched = _advisor_match(question, ranked); st.markdown("### Cortex Analysis")
    if matched is None:
        st.write(response["answer"]); render_confidence_panel(response["confidence"], [])
        if response.get("details"):
            with st.expander("Analysis details", expanded=False):
                for detail in response["details"]: st.write(f"• {detail}")
        return
    player, team, data = matched; score = float(data.get("adjusted_score", data.get("score", 0.0))); recommendation = recommendation_from_score(score); signals = data.get("signals", [])
    st.markdown(f"## {player} · {team}"); col1, col2, col3 = st.columns(3); col1.metric("Recommendation", recommendation); col2.metric("Cortex Score", f"{score:+.2f}"); col3.metric("Signals", len(signals)); st.write(response["answer"]); render_confidence_panel(response["confidence"], signals)
    st.markdown("### Why Cortex recommends this")
    if signals:
        for signal in sorted(signals, key=lambda signal: abs(float(signal.get("value", 0.0))), reverse=True)[:4]:
            value = float(signal.get("value", 0.0)); direction = "Positive" if value > 0 else "Negative" if value < 0 else "Neutral"; st.write(f"• **{direction} {value:+.2f}** — {signal.get('headline', 'Signal')}")
    else: st.info("No scored supporting signals are available yet.")
    render_signal_breakdown(signals); _render_intelligence_bars(data); render_cortex_timeline(signals); st.markdown("### Supporting Headlines")
    if signals:
        for signal in reversed(signals[-5:]): st.markdown(f"**{signal.get('headline', 'Signal')}**"); st.caption(f"{signal.get('source', 'Unknown source')} · {signal.get('impact', 'unknown')} · {float(signal.get('value', 0.0)):+.2f}")
    else: st.info("No supporting headlines are available yet.")
    with st.expander("Developer / Cortex workflow", expanded=False):
        for detail in response.get("details", []): st.write(f"• {detail}")
        st.divider()
        for step in ("Interpret question", "Identify players/teams", "Search scorecards", "Expand knowledge graph", "Evaluate propagation", "Generate recommendation", "Explain reasoning"): st.write(f"• {step}")


st.set_page_config(page_title="GridironGPT | Cortex Engine", page_icon="C", layout="wide", initial_sidebar_state="expanded")
apply_cortex_theme(); catalog = load_player_catalog(); player_names = sorted({item["player"] for item in catalog}); positions = {item["player"]: item.get("position", "UNK") for item in catalog}; scores = apply_adjusted_scores(calculate_player_scores()); ranked_players = sorted(scores.items(), key=lambda item: item[1].get("adjusted_score", item[1]["score"]), reverse=True); ranked_players = [((player, team), data) for (player, team), data in ranked_players if data["score"] != 0]
roster_advisor = RosterAdvisor(ranked_players=ranked_players, recommendation_from_score=recommendation_from_score, confidence_from_signals=confidence_from_signals)
if "cortex_facade" not in st.session_state:
    st.session_state.cortex_facade = CortexFacade()
cortex = st.session_state.cortex_facade
activity_feed = ActivityFeedService(cortex.event_bus)
buy_players = [((player, team), data) for (player, team), data in ranked_players if recommendation_from_score(data.get("adjusted_score", data["score"])) == "BUY"]; watch_players = [((player, team), data) for (player, team), data in ranked_players if recommendation_from_score(data.get("adjusted_score", data["score"])) == "WATCH"]; risk_players = [((player, team), data) for (player, team), data in ranked_players if recommendation_from_score(data.get("adjusted_score", data["score"])) in ["MONITOR", "SELL"]]
version = get_project_version(); selected_page = render_sidebar(version=version); page_metadata = NAVIGATION_ITEMS[selected_page]; render_shell_header(page_name=page_metadata["label"], description=page_metadata["description"]); st.divider()

if selected_page == "Inspector": render_cortex_inspector(cortex)
if selected_page == "Ingestion": render_ingestion_status()
if selected_page == "Explorer": render_cortex_explorer(player_names, cortex)
if selected_page == "Dashboard":
    dashboard = build_dashboard_view_model(ranked_players=ranked_players, buy_players=buy_players, watch_players=watch_players, risk_players=risk_players, player_count=len(player_names), recommendation_from_score=recommendation_from_score, confidence_from_signals=confidence_from_signals, passing_tests=702); render_dashboard(dashboard, scores=scores, positions=positions, activity_groups=activity_feed.latest(limit=10))
if selected_page == "Advisor":
    st.markdown("### Ask Cortex"); st.caption("Ask football questions in natural language."); question = st.text_area("Ask Gridiron Cortex", placeholder="Examples:\n• Who should I start this week?\n• Best waiver pickup over the next 3 weeks?\n• Should I trade Tank Dell?\n• Best DST to stream next week?", height=140)
    if st.button("Ask Cortex", use_container_width=True):
        if question.strip(): _render_advisor_result(question, roster_advisor.answer(question), ranked_players)
        else: st.warning("Enter a question first.")
if selected_page == "Players":
    st.markdown("### Player Intelligence"); default_player = "Tank Dell" if "Tank Dell" in player_names else player_names[0]; selected_player = st.selectbox("Select player", player_names, index=player_names.index(default_player)); intel = build_player_intelligence(selected_player)
    if intel["status"] == "not_found": st.warning(f"No intelligence found for {selected_player}.")
    else:
        col1, col2, col3 = st.columns(3); col1.metric("Recommendation", intel["recommendation"]); col2.metric("Score", f"{intel['score']:+.2f}"); col3.metric("Confidence", f"{intel['confidence']}%"); st.divider(); st.markdown("### 🚀 Momentum"); momentum = intel["momentum"]
        if momentum.get("status") == "first_snapshot": st.info("First snapshot recorded. More history is needed for momentum.")
        elif momentum.get("status") == "ok": st.metric("Momentum Score", f"{momentum.get('momentum_score', 0):+.2f}", delta=momentum.get("direction", "stable")); st.write(f"Direction: **{momentum.get('direction', 'stable').upper()}**")
        else: st.info("No momentum history available yet.")
        st.divider(); st.markdown("### 📈 Trend"); trend = intel["trend"]
        if trend.get("status") == "first_snapshot": st.info("First trend snapshot recorded. More history is needed.")
        elif trend.get("status") == "ok": st.write(f"Current Score: `{trend.get('current_score')}`"); st.write(f"Previous Score: `{trend.get('previous_score')}`"); st.write(f"Change: `{trend.get('change'):+.2f}`"); st.write(f"Direction: **{trend.get('direction', 'stable').upper()}**")
        else: st.info("No trend history available yet.")
        st.divider(); st.markdown("### 📰 Recent Signals"); recent_signals = intel.get("recent_signals", [])
        if recent_signals:
            for signal in recent_signals: st.write(f"- **[{signal.get('source')}]** `{signal.get('impact')}` `{signal.get('value'):+.2f}` — {signal.get('headline')}")
        else: st.info("No recent signals found.")
if selected_page == "Trends":
    st.markdown("### Trending Players"); hot_players = []; cold_players = []
    for (player, team), data in scores.items():
        velocity = calculate_velocity(player); confidence = confidence_from_signals(data["signals"]); item = {"player": player, "team": team, "velocity": velocity["velocity"], "direction": velocity["direction"], "confidence": confidence, "score": data["score"]}
        if velocity["velocity"] > 0: hot_players.append(item)
        if velocity["velocity"] < 0: cold_players.append(item)
    hot_players.sort(key=lambda item: item["velocity"], reverse=True); cold_players.sort(key=lambda item: item["velocity"]); col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔥 Hot Players")
        if hot_players:
            for item in hot_players[:5]: st.metric(label=f"{item['player']} ({item['team']})", value=f"{item['velocity']:+.2f}/week", delta=f"{item['confidence']}% confidence")
        else: st.info("No hot players found.")
    with col2:
        st.markdown("### 🧊 Cold Players")
        if cold_players:
            for item in cold_players[:5]: st.metric(label=f"{item['player']} ({item['team']})", value=f"{item['velocity']:+.2f}/week", delta=f"{item['confidence']}% confidence")
        else: st.info("No cooling players found.")
if selected_page == "Trajectory":
    st.subheader("🚀 Trajectory"); rankings = build_momentum_rankings(limit=10); col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Risers")
        if rankings["risers"]:
            for item in rankings["risers"]: st.metric(label=f"{item['player']} ({item.get('team') or 'UNK'})", value=f"{item['current_score']:+.2f}", delta=f"{item['change']:+.2f}"); st.caption(f"Velocity: {item['velocity']:+.2f}")
        else: st.info("No risers yet. More score snapshots are needed.")
    with col2:
        st.markdown("### Top Fallers")
        if rankings["fallers"]:
            for item in rankings["fallers"]: st.metric(label=f"{item['player']} ({item.get('team') or 'UNK'})", value=f"{item['current_score']:+.2f}", delta=f"{item['change']:+.2f}"); st.caption(f"Velocity: {item['velocity']:+.2f}")
        else: st.info("No fallers yet. More score snapshots are needed.")
    st.divider(); st.markdown("### 🆕 First Snapshots")
    if rankings["first_snapshots"]:
        for item in rankings["first_snapshots"]: st.write(f"- **{item['player']} ({item.get('team') or 'UNK'})** — Current Score: `{float(item.get('current_score') or 0):+.2f}`")
    else: st.info("No first snapshots found.")
