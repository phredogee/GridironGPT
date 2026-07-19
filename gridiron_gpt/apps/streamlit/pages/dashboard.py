from __future__ import annotations

import streamlit as st

from apps.streamlit.view_models.dashboard import (
    DashboardPlayer,
    DashboardViewModel,
)
from apps.streamlit.components.player_card import (
    render_player_card,
)
from apps.streamlit.components.metrics_panel import (
    render_metrics_panel,
)
from apps.streamlit.components.rankings_table import (
    render_rankings_table,
)

def _inject_dashboard_styles() -> None:
    """Apply styles used only by the Dashboard page."""

    st.markdown(
        """
        <style>
        .dashboard-eyebrow {
            color: #4ade80;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-bottom: 0.15rem;
            text-transform: uppercase;
        }

        .dashboard-title {
            font-size: 1.45rem;
            font-weight: 750;
            line-height: 1.2;
            margin-bottom: 0.2rem;
        }

        .dashboard-description {
            color: rgba(250, 250, 250, 0.62);
            font-size: 0.88rem;
            margin-bottom: 1rem;
        }

        .dashboard-badge {
            border-radius: 999px;
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            padding: 0.24rem 0.58rem;
            text-transform: uppercase;
        }

        .dashboard-badge-buy {
            background: rgba(74, 222, 128, 0.12);
            border: 1px solid rgba(74, 222, 128, 0.35);
            color: #4ade80;
        }

        .dashboard-badge-watch {
            background: rgba(250, 204, 21, 0.12);
            border: 1px solid rgba(250, 204, 21, 0.35);
            color: #facc15;
        }

        .dashboard-badge-risk {
            background: rgba(248, 113, 113, 0.12);
            border: 1px solid rgba(248, 113, 113, 0.35);
            color: #f87171;
        }

        .dashboard-badge-neutral {
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
        }

        .dashboard-player-name {
            font-size: 1.12rem;
            font-weight: 750;
            margin-top: 0.65rem;
        }

        .dashboard-player-team {
            color: rgba(250, 250, 250, 0.58);
            font-size: 0.8rem;
            margin-bottom: 0.7rem;
        }

        .dashboard-empty-state {
            color: rgba(250, 250, 250, 0.58);
            font-size: 0.86rem;
            padding: 1rem 0;
            text-align: center;
        }

        .dashboard-ranking-name {
            font-size: 0.9rem;
            font-weight: 700;
        }

        .dashboard-ranking-team {
            color: rgba(250, 250, 250, 0.55);
            font-size: 0.72rem;
        }

        .dashboard-ranking-value {
            font-size: 0.86rem;
            font-weight: 700;
            padding-top: 0.2rem;
            text-align: right;
        }

        .dashboard-system-health {
            color: rgba(250, 250, 250, 0.6);
            font-size: 0.78rem;
            padding: 0.3rem 0;
            text-align: center;
        }

        .dashboard-system-online {
            color: #4ade80;
            font-weight: 750;
        }

        div[data-testid="stMetric"] {
            background: rgba(18, 28, 22, 0.72);
            border: 1px solid rgba(74, 222, 128, 0.14);
            border-radius: 10px;
            padding: 0.85rem 1rem;
        }

        div[data-testid="stMetricLabel"] {
            color: rgba(250, 250, 250, 0.58);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(18, 28, 22, 0.55);
            border-color: rgba(74, 222, 128, 0.16);
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _render_section_header(
    *,
    label: str,
    title: str,
    description: str | None = None,
) -> None:
    """Render a consistent Dashboard section heading."""

    st.markdown(
        f'<div class="dashboard-eyebrow">{label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="dashboard-title">{title}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.markdown(
            f'<div class="dashboard-description">{description}</div>',
            unsafe_allow_html=True,
        )


def _render_top_candidates(view_model: DashboardViewModel) -> None:
    """Render the top BUY, WATCH, and RISK players."""

    buy_col, watch_col, risk_col = st.columns(3)

    with buy_col:
        render_player_card(
            view_model.top_buy,
            title="Top Buy",
        )

    with watch_col:
        render_player_card(
            view_model.top_watch,
            title="Watch List",
        )

    with risk_col:
        render_player_card(
            view_model.top_risk,
            title="Highest Risk",
        )


def _render_system_health(view_model: DashboardViewModel) -> None:
    """Render the compact Dashboard system-health line."""

    test_label = "test" if view_model.passing_tests == 1 else "tests"

    st.markdown(
        f"""
        <div class="dashboard-system-health">
            <span class="dashboard-system-online">Operational</span>
            &nbsp;|&nbsp;
            Cortex pipeline active
            &nbsp;|&nbsp;
            {view_model.passing_tests} passing {test_label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(view_model: DashboardViewModel) -> None:
    """
    Render the GridironGPT Dashboard.

    All business and transformation logic is handled before this function
    receives the DashboardViewModel.
    """

    _inject_dashboard_styles()

    _render_section_header(
        label="Command Center",
        title="Fantasy intelligence at a glance",
        description=(
            "Review current player coverage, recommendation activity, "
            "and the strongest fantasy signals."
        ),
    )

    render_metrics_panel(view_model.summary)
    
    st.write("")

    _render_section_header(
        label="Recommendations",
        title="Leading opportunities and risks",
        description=(
            "The highest-ranked player currently available in each "
            "recommendation group."
        ),
    )

    _render_top_candidates(view_model)

    st.write("")

    _render_section_header(
        label="Rankings",
        title="Top signal rankings",
        description=(
            "Players ranked by adjusted score, confidence, and current "
            "Cortex recommendation."
        ),
    )

    render_rankings_table(view_model.rankings)
    
    st.divider()

    _render_system_health(view_model)
