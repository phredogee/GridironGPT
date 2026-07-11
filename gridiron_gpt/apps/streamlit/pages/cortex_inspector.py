import pandas as pd
import streamlit as st

from gridiron_cortex.models.raw_event import RawEvent
from apps.streamlit.components.player_scorecard import render_player_scorecard
from apps.streamlit.components.pipeline_status import render_pipeline_status
from apps.streamlit.components.recommendation_card import render_recommendation_card
from apps.streamlit.components.explanation_panel import render_explanation_panel
from apps.streamlit.components.engine_diagnostics import (
    render_engine_diagnostics,
)
from apps.streamlit.components.signal_summary import (
    render_signal_summary,
)
from apps.streamlit.components.player_timeline import (
    render_player_timeline,
)


def render_cortex_inspector(cortex):
    st.subheader("🧠 Cortex Inspector")
    st.caption("Inspect the typed Cortex intelligence pipeline step by step.")

    st.markdown("### Input Event")

    headline = st.text_input(
        "Headline",
        value="Tank Dell returns to practice and is running with the first-team offense.",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        player = st.text_input("Player", value="Tank Dell")

    with col2:
        team = st.text_input("Team", value="HOU")

    with col3:
        source = st.text_input("Source", value="manual")

    if st.button("Analyze Event"):
        event = RawEvent(
            headline=headline,
            source=source,
            player=player or None,
            team=team or None,
        )

        result = cortex.process_event(event)

        st.divider()

        render_pipeline_status(result)

        st.divider()
        render_signal_summary(result)

        st.divider()
        render_player_scorecard(result)

        st.divider()
        render_player_timeline(result)

        st.divider()
        render_recommendation_card(result)

        st.divider()
        render_explanation_panel(result)

        st.divider()
        render_engine_diagnostics(result)
