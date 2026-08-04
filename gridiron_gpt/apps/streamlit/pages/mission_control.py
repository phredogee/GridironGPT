from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from apps.streamlit.components.activity_feed import render_activity_feed
from apps.streamlit.components.player_card import render_player_card
from gridiron_cortex.activity.activity_feed_service import ActivityFeedService


@dataclass(frozen=True, slots=True)
class MissionControlStatus:
    event_count: int
    relationship_count: int
    player_count: int
    scored_player_count: int
    passing_tests: int


def build_mission_control_status(
    *,
    event_count: int,
    relationship_count: int,
    player_count: int,
    scored_player_count: int,
    passing_tests: int,
) -> MissionControlStatus:
    return MissionControlStatus(
        event_count=max(0, event_count),
        relationship_count=max(0, relationship_count),
        player_count=max(0, player_count),
        scored_player_count=max(0, scored_player_count),
        passing_tests=max(0, passing_tests),
    )


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .mc-kicker{color:#79ff9f;font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
        .mc-title{font-size:2rem;font-weight:800;letter-spacing:-.03em;margin:.15rem 0 .25rem}
        .mc-subtitle{color:rgba(245,250,247,.62);font-size:.92rem;margin-bottom:1.1rem}
        .mc-panel-title{font-size:1rem;font-weight:750;margin-bottom:.45rem}
        .mc-status{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.55rem;margin-top:1rem}
        .mc-status-card{background:rgba(15,28,20,.86);border:1px solid rgba(82,214,124,.18);border-radius:10px;padding:.75rem .8rem;text-align:center}
        .mc-status-label{color:rgba(245,250,247,.55);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase}
        .mc-status-value{color:#fff;font-size:1.08rem;font-weight:800;margin-top:.15rem}
        .mc-online{color:#79ff9f}
        @media(max-width:900px){.mc-status{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_status_strip(status: MissionControlStatus) -> None:
    items = (
        ("Event Bus", f"{status.event_count} events", True),
        ("Knowledge Graph", f"{status.relationship_count} links", True),
        ("Players", str(status.player_count), True),
        ("Scored", str(status.scored_player_count), True),
        ("Regression", f"{status.passing_tests} passed", True),
    )
    cards = []
    for label, value, online in items:
        value_class = "mc-status-value mc-online" if online else "mc-status-value"
        cards.append(
            f'<div class="mc-status-card"><div class="mc-status-label">{label}</div>'
            f'<div class="{value_class}">{value}</div></div>'
        )
    st.markdown(f'<div class="mc-status">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_mission_control(
    *,
    cortex,
    dashboard,
    player_count: int,
    scored_player_count: int,
    passing_tests: int,
) -> None:
    """Render the flagship Cortex operations console."""
    _inject_styles()
    st.markdown('<div class="mc-kicker">Cortex Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="mc-title">Mission Control</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mc-subtitle">Live reasoning activity, recommendation priorities, and platform health from one operational view.</div>',
        unsafe_allow_html=True,
    )

    activity_service = ActivityFeedService(cortex.event_bus)
    activity_groups = activity_service.latest(limit=8)

    left, right = st.columns([1.15, .85])
    with left:
        st.markdown('<div class="mc-panel-title">Live Cortex Activity</div>', unsafe_allow_html=True)
        render_activity_feed(activity_groups, empty_message="No Cortex events have been processed in this session yet.")
    with right:
        st.markdown('<div class="mc-panel-title">Recommendation Center</div>', unsafe_allow_html=True)
        render_player_card(dashboard.top_buy, title="Top Buy")
        render_player_card(dashboard.top_watch, title="Watch List")
        render_player_card(dashboard.top_risk, title="Highest Risk")

    st.divider()
    st.markdown('<div class="mc-panel-title">Operational Snapshot</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ranked Players", len(dashboard.rankings))
    m2.metric("Tracked Players", player_count)
    m3.metric("Scored Players", scored_player_count)
    m4.metric("Activity Stories", len(activity_groups))

    relationships = cortex.knowledge.get_current_relationships()
    status = build_mission_control_status(
        event_count=len(cortex.get_event_history()),
        relationship_count=len(relationships),
        player_count=player_count,
        scored_player_count=scored_player_count,
        passing_tests=passing_tests,
    )
    _render_status_strip(status)
