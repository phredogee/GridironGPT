from __future__ import annotations

import streamlit as st

from apps.streamlit.view_models.dashboard import DashboardSummary


def render_metrics_panel(summary: DashboardSummary) -> None:
    """
    Render the Dashboard summary metrics.

    The component only renders values already prepared by the
    Dashboard view model.
    """

    player_col, buy_col, watch_col, risk_col = st.columns(4)

    with player_col:
        st.metric(
            label="Tracked Players",
            value=summary.player_count,
        )

    with buy_col:
        st.metric(
            label="Buy Signals",
            value=summary.buy_count,
        )

    with watch_col:
        st.metric(
            label="Watch Signals",
            value=summary.watch_count,
        )

    with risk_col:
        st.metric(
            label="Risk Signals",
            value=summary.risk_count,
        )
