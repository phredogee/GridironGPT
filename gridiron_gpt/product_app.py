from __future__ import annotations

import streamlit as st

from apps.streamlit.components.theme import apply_cortex_theme
from apps.streamlit.pages.commissioner_hub import render_commissioner_hub
from apps.streamlit.pages.decision_center import render_decision_center
from apps.streamlit.pages.league_settings import render_league_settings
from apps.streamlit.pages.schedule_generator import render_schedule_generator
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
)
from gridiron_gpt.product.decision_player_pool import build_decision_player_pool


st.set_page_config(
    page_title="GridironGPT Decision Center",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_cortex_theme()

st.sidebar.title("GridironGPT")
page = st.sidebar.radio(
    "Product",
    [
        "Decision Center",
        "Commissioner Hub",
        "League Settings",
        "Schedule Generator",
        "API",
    ],
)

catalog = load_player_catalog()
score_data = calculate_player_scores()
players = build_decision_player_pool(
    catalog,
    score_data,
    confidence_from_signals=confidence_from_signals,
)

if page == "Decision Center":
    render_decision_center(players)
elif page == "Commissioner Hub":
    render_commissioner_hub(players)
elif page == "League Settings":
    render_league_settings()
elif page == "Schedule Generator":
    render_schedule_generator()
else:
    st.markdown("### REST API")
    st.code("uvicorn gridiron_gpt.api.app:app --reload", language="bash")
    st.write("Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`")
    st.write("Health check: `GET /health`")
    st.write("Schedule generator: `POST /schedules/generate`")
    st.write("Schedule email: `POST /schedules/email`")
