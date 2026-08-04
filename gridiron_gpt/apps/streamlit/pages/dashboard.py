from __future__ import annotations

import streamlit as st

from apps.streamlit.view_models.dashboard import DashboardViewModel
from apps.streamlit.components.player_card import render_player_card
from apps.streamlit.components.metrics_panel import render_metrics_panel
from apps.streamlit.components.rankings_table import render_rankings_table
from apps.streamlit.components.intelligence_charts import render_platform_charts
from apps.streamlit.components.activity_feed import render_activity_feed
from gridiron_cortex.activity.activity_models import ActivityGroup


def _inject_dashboard_styles() -> None:
    st.markdown(
        """
        <style>
        .dashboard-eyebrow {color:#4ade80;font-size:.72rem;font-weight:700;letter-spacing:.12em;margin-bottom:.15rem;text-transform:uppercase;}
        .dashboard-title {font-size:1.45rem;font-weight:750;line-height:1.2;margin-bottom:.2rem;}
        .dashboard-description {color:rgba(250,250,250,.62);font-size:.88rem;margin-bottom:1rem;}
        .dashboard-system-health {color:rgba(250,250,250,.6);font-size:.78rem;padding:.3rem 0;text-align:center;}
        .dashboard-system-online {color:#4ade80;font-weight:750;}
        div[data-testid="stMetric"] {background:rgba(18,28,22,.72);border:1px solid rgba(74,222,128,.14);border-radius:10px;padding:.85rem 1rem;}
        div[data-testid="stMetricLabel"] {color:rgba(250,250,250,.58);}
        div[data-testid="stVerticalBlockBorderWrapper"] {background:rgba(18,28,22,.55);border-color:rgba(74,222,128,.16);border-radius:10px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_section_header(*, label: str, title: str, description: str | None = None) -> None:
    st.markdown(f'<div class="dashboard-eyebrow">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-title">{title}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="dashboard-description">{description}</div>', unsafe_allow_html=True)


def _render_top_candidates(view_model: DashboardViewModel) -> None:
    buy_col, watch_col, risk_col = st.columns(3)
    with buy_col:
        render_player_card(view_model.top_buy, title="Top Buy")
    with watch_col:
        render_player_card(view_model.top_watch, title="Watch List")
    with risk_col:
        render_player_card(view_model.top_risk, title="Highest Risk")


def _render_system_health(view_model: DashboardViewModel) -> None:
    test_label = "test" if view_model.passing_tests == 1 else "tests"
    st.markdown(
        f"""
        <div class="dashboard-system-health">
            <span class="dashboard-system-online">Operational</span>
            &nbsp;|&nbsp; Cortex pipeline active
            &nbsp;|&nbsp; {view_model.passing_tests} passing {test_label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(
    view_model: DashboardViewModel,
    *,
    scores: dict | None = None,
    positions: dict[str, str] | None = None,
    activity_groups: tuple[ActivityGroup, ...] | None = None,
) -> None:
    """Render the GridironGPT live intelligence command center."""
    _inject_dashboard_styles()

    _render_section_header(
        label="Command Center",
        title="Fantasy intelligence at a glance",
        description="Live Cortex scoring, recommendation activity, team momentum, and player rankings.",
    )
    render_metrics_panel(view_model.summary)
    st.write("")

    if activity_groups is not None:
        _render_section_header(
            label="Event Stream",
            title="Watch Cortex reason",
            description="Correlated engine events show how each article becomes entities, signals, propagation, scores, and recommendations.",
        )
        render_activity_feed(activity_groups)
        st.write("")

    _render_section_header(
        label="Recommendations",
        title="Leading opportunities and risks",
        description="The highest-ranked player currently available in each recommendation group.",
    )
    _render_top_candidates(view_model)
    st.write("")

    if scores is not None and positions is not None:
        _render_section_header(
            label="Live Analytics",
            title="Cortex market view",
            description="Recommendation distribution, team momentum, and position-specific rankings from current scored signals.",
        )
        render_platform_charts(scores, positions)
        st.write("")

    _render_section_header(
        label="Rankings",
        title="Top signal rankings",
        description="Players ranked by adjusted score, confidence, and current Cortex recommendation.",
    )
    render_rankings_table(view_model.rankings)
    st.divider()
    _render_system_health(view_model)
