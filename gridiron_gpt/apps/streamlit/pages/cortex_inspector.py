import streamlit as st

from apps.streamlit.components.cognitive_trace import (
    render_cognitive_trace,
)
from apps.streamlit.components.cortex_panel import (
    cortex_panel,
)
from apps.streamlit.components.engine_diagnostics import (
    render_engine_diagnostics,
)
from apps.streamlit.components.evidence_graph_panel import (
    render_evidence_graph_panel,
)
from apps.streamlit.components.explanation_panel import (
    render_explanation_panel,
)
from apps.streamlit.components.pipeline_status import (
    render_pipeline_status,
)
from apps.streamlit.components.player_snapshot import (
    render_player_snapshot,
)
from apps.streamlit.components.player_timeline import (
    render_player_timeline,
)
from apps.streamlit.components.prediction_panel import (
    render_prediction_panel,
)
from apps.streamlit.components.recommendation_card import (
    render_recommendation_card,
)
from apps.streamlit.components.signal_summary import (
    render_signal_summary,
)
from gridiron_cortex.models.raw_event import RawEvent


def render_cortex_inspector(cortex):
    st.html(
        """
        <div class="cortex-page-heading">
            <div class="cortex-page-title">
                Cortex Inspector 2.0
            </div>
            <div class="cortex-page-subtitle">
                Inspect recommendations, predictions, evidence,
                and the complete Cortex reasoning path.
            </div>
        </div>
        """
    )
 

    st.markdown("### Input Event")

    with cortex_panel(
        title="Input Event",
        subtitle=(
            "Submit a football event to inspect the complete "
            "Cortex reasoning pipeline."
        ),
    ):
        headline = st.text_input(
            "Headline",
            value=(
                "Tank Dell returns to practice and is running "
                "with the first-team offense."
            ),
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            player = st.text_input(
                "Player",
                value="Tank Dell",
            )

        with col2:
            team = st.text_input(
                "Team",
                value="HOU",
            )

        with col3:
            source = st.text_input(
                "Source",
                value="manual",
            )

        analyze = st.button(
            "Analyze Event",
            type="primary",
        )

    if analyze:
        event = RawEvent(
            headline=headline,
            source=source,
            player=player or None,
            team=team or None,
        )

        st.session_state["cortex_inspector_result"] = (
            cortex.process_event(event)
        )

    result = st.session_state.get(
        "cortex_inspector_result"
    )

    if result is None:
        st.info(
            "Enter an event and select Analyze Event "
            "to inspect the cognitive pipeline."
        )
        return

    st.divider()

    if result.explanation == "Duplicate event ignored.":
        st.warning(
            "This event was already processed. Change the "
            "headline or source to generate a new result."
        )

    render_pipeline_status(result)

    st.divider()

    (
        summary_tab,
        trace_tab,
        graph_tab,
        intelligence_tab,
        explanation_tab,
        diagnostics_tab,
    ) = st.tabs(
        [
            "Summary",
            "Cognitive Trace",
            "Evidence Graph",
            "Intelligence",
            "Explanation",
            "Diagnostics",
        ]
    )

    with summary_tab:
        render_signal_summary(result)
        st.divider()
        render_recommendation_card(result)

    with trace_tab:
        render_cognitive_trace(result)

    with graph_tab:
        render_evidence_graph_panel(result)

    with intelligence_tab:
        render_prediction_panel(result)
        st.divider()
        render_player_snapshot(result)
        st.divider()
        render_player_timeline(result)

    with explanation_tab:
        render_explanation_panel(result)

    with diagnostics_tab:
        render_engine_diagnostics(result)
