from __future__ import annotations

import streamlit as st

from apps.streamlit.components.theme import apply_cortex_theme
from apps.streamlit.pages.decision_center import render_decision_center
from apps.streamlit.pages.league_settings import render_league_settings
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
)
from gridiron_gpt.fantasy_decisions.models import PlayerDecisionInput


st.set_page_config(
    page_title="GridironGPT Decision Center",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_cortex_theme()

st.sidebar.title("GridironGPT")
page = st.sidebar.radio("Product", ["Decision Center", "League Settings", "API"])

catalog = load_player_catalog()
score_data = calculate_player_scores()
lookup = {item["player"]: item for item in catalog}

players = []
for (name, team), data in score_data.items():
    catalog_item = lookup.get(name, {})
    score = float(data.get("score", 0.0))
    players.append(
        PlayerDecisionInput(
            player_id=str(catalog_item.get("player_id") or name.casefold().replace(" ", "-")),
            player_name=name,
            position=str(catalog_item.get("position") or "UNK"),
            team=team,
            cortex_score=score,
            confidence=confidence_from_signals(data.get("signals", [])) / 100.0,
            projected_points=max(0.0, 10.0 + score),
            replacement_value=max(0.0, score / 2.0),
            evidence={"signals": data.get("signals", [])},
        )
    )

if page == "Decision Center":
    render_decision_center(players)
elif page == "League Settings":
    render_league_settings()
else:
    st.markdown("### REST API")
    st.code("uvicorn gridiron_gpt.api.app:app --reload", language="bash")
    st.write("Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`")
    st.write("Health check: `GET /health`")
