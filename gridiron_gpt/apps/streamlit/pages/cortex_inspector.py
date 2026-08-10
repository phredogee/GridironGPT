import streamlit as st

from apps.streamlit.components.cognitive_trace import (
    render_cognitive_trace,
)
from apps.streamlit.components.confidence_panel import (
    render_confidence_panel,
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
from apps.streamlit.components.propagation_panel import (
    render_propagation_panel,
)
from apps.streamlit.components.recommendation_card import (
    render_recommendation_card,
)
from apps.streamlit.components.signal_summary import (
    render_signal_summary,
)
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.data_ingest.player_catalog import (
    load_player_catalog,
)


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

    # ------------------------------------------------------------------
    # Player catalog
    # ------------------------------------------------------------------

    catalog = load_player_catalog()

    fantasy_players = [
        player
        for player in catalog
        if player.get("position") in {"QB", "RB", "WR", "TE"}
        and player.get("status") == "ACT"
    ]

    fantasy_players = sorted(
        fantasy_players,
        key=lambda player: player["player"].casefold(),
    )

    player_options = {
        (
            f'{player["player"]} — '
            f'{player.get("team") or "UNK"} — '
            f'{player.get("position") or "UNK"}'
        ): player
        for player in fantasy_players
    }

    # ------------------------------------------------------------------
    # Input event
    # ------------------------------------------------------------------

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

        if not player_options:
            st.warning(
                "No active fantasy players are available in "
                "the player catalog."
            )
            return

        selected_label = st.selectbox(
            "Player",
            options=list(player_options.keys()),
            index=None,
            placeholder="Search NFL players...",
        )

        selected_player = (
            player_options[selected_label]
            if selected_label is not None
            else None
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            team = (
                selected_player.get("team") or ""
                if selected_player
                else ""
            )

            st.text_input(
                "Team",
                value=team,
                disabled=True,
            )

        with col2:
            position = (
                selected_player.get("position") or ""
                if selected_player
                else ""
            )

            st.text_input(
                "Position",
                value=position,
                disabled=True,
            )

        with col3:
            source = st.text_input(
                "Source",
                value="manual",
            )

        analyze = st.button(
            "Analyze Event",
            type="primary",
            disabled=selected_player is None,
        )

    # ------------------------------------------------------------------
    # Run Cortex
    # ------------------------------------------------------------------

    if analyze and selected_player is not None:
        event = RawEvent(
            headline=headline,
            source=source,
            player=selected_player["player"],
            team=selected_player.get("team") or None,
        )

        st.session_state["cortex_inspector_result"] = (
            cortex.process_event(event)
        )

    result = st.session_state.get(
        "cortex_inspector_result"
    )

    if result is None:
        st.info(
            "Select a player, enter an event, and select Analyze Event "
            "to inspect the cognitive pipeline."
        )
        return

    st.divider()

    # ------------------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------------------

    if result.explanation == "Duplicate event ignored.":
        st.warning(
            "This event was already processed. Change the "
            "headline or source to generate a new result."
        )

    # ------------------------------------------------------------------
    # Pipeline status
    # ------------------------------------------------------------------

    render_pipeline_status(result)

    st.divider()

    # ------------------------------------------------------------------
    # Inspector tabs
    # ------------------------------------------------------------------

    (
        summary_tab,
        confidence_tab,
        trace_tab,
        graph_tab,
        propagation_tab,
        intelligence_tab,
        explanation_tab,
        diagnostics_tab,
    ) = st.tabs(
        [
            "Summary",
            "Evidence & Confidence",
            "Cognitive Trace",
            "Evidence Graph",
            "Propagation",
            "Intelligence",
            "Explanation",
            "Diagnostics",
        ]
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    with summary_tab:
        render_signal_summary(result)

        st.divider()

        render_recommendation_card(result)

    # ------------------------------------------------------------------
    # Evidence & Confidence
    # ------------------------------------------------------------------

    with confidence_tab:
        render_confidence_panel(result)

    # ------------------------------------------------------------------
    # Cognitive Trace
    # ------------------------------------------------------------------

    with trace_tab:
        render_cognitive_trace(result)

    # ------------------------------------------------------------------
    # Evidence Graph
    # ------------------------------------------------------------------

    with graph_tab:
        render_evidence_graph_panel(result)

    # ------------------------------------------------------------------
    # Propagation
    #-------------------------------------------------------------------

    with propagation_tab:
        render_propagation_panel(result)

    # ------------------------------------------------------------------
    # Intelligence
    # ------------------------------------------------------------------

    with intelligence_tab:
        render_prediction_panel(result)

        st.divider()

        render_player_snapshot(result)

        st.divider()

        render_player_timeline(result)

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    with explanation_tab:
        render_explanation_panel(result)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    with diagnostics_tab:
        render_engine_diagnostics(result)
