from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import streamlit as st

from apps.streamlit.components.activity_feed import render_activity_feed
from apps.streamlit.components.knowledge_graph import render_knowledge_graph
from apps.streamlit.components.player_card import render_player_card
from gridiron_cortex.activity.activity_feed_service import ActivityFeedService
from gridiron_gpt.intelligence.explorer_graph import build_explorer_graph
from gridiron_gpt.intelligence.explorer_relationships import (
    build_propagation_rows,
    find_entity_id,
)


@dataclass(frozen=True, slots=True)
class MissionControlStatus:
    event_count: int
    relationship_count: int
    player_count: int
    scored_player_count: int
    passing_tests: int


@dataclass(frozen=True, slots=True)
class MissionPlayerContext:
    player: str
    team: str
    score: float
    signal_count: int
    entity_id: str | None


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


def build_player_contexts(
    scores: Mapping[tuple[str, str], dict],
    relationships,
) -> tuple[MissionPlayerContext, ...]:
    contexts = [
        MissionPlayerContext(
            player=player,
            team=team,
            score=float(data.get("adjusted_score", data.get("score", 0.0))),
            signal_count=len(data.get("signals", [])),
            entity_id=find_entity_id(player, relationships),
        )
        for (player, team), data in scores.items()
        if float(data.get("adjusted_score", data.get("score", 0.0))) != 0
    ]
    return tuple(sorted(contexts, key=lambda item: (-item.score, item.player)))


def select_default_context(
    contexts: tuple[MissionPlayerContext, ...],
) -> MissionPlayerContext | None:
    if not contexts:
        return None
    connected = next((item for item in contexts if item.entity_id), None)
    return connected or contexts[0]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .mc-kicker{color:#79ff9f;font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
        .mc-title{font-size:2rem;font-weight:800;letter-spacing:-.03em;margin:.15rem 0 .25rem}
        .mc-subtitle{color:rgba(245,250,247,.62);font-size:.92rem;margin-bottom:1.1rem}
        .mc-panel-title{font-size:1rem;font-weight:750;margin-bottom:.45rem}
        .mc-context{background:linear-gradient(90deg,rgba(22,74,42,.62),rgba(11,25,17,.72));border:1px solid rgba(121,255,159,.22);border-radius:12px;padding:.85rem 1rem;margin:.3rem 0 1rem}
        .mc-context-name{font-size:1.1rem;font-weight:800;color:#fff}.mc-context-meta{color:rgba(245,250,247,.62);font-size:.8rem;margin-top:.15rem}
        .mc-status{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.55rem;margin-top:1rem}
        .mc-status-card{background:rgba(15,28,20,.86);border:1px solid rgba(82,214,124,.18);border-radius:10px;padding:.75rem .8rem;text-align:center}
        .mc-status-label{color:rgba(245,250,247,.55);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase}
        .mc-status-value{color:#fff;font-size:1.08rem;font-weight:800;margin-top:.15rem}.mc-online{color:#79ff9f}
        @media(max-width:900px){.mc-status{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_status_strip(status: MissionControlStatus) -> None:
    items = (
        ("Event Bus", f"{status.event_count} events"),
        ("Knowledge Graph", f"{status.relationship_count} links"),
        ("Players", str(status.player_count)),
        ("Scored", str(status.scored_player_count)),
        ("Regression", f"{status.passing_tests} passed"),
    )
    cards = [
        f'<div class="mc-status-card"><div class="mc-status-label">{label}</div>'
        f'<div class="mc-status-value mc-online">{value}</div></div>'
        for label, value in items
    ]
    st.markdown(f'<div class="mc-status">{"".join(cards)}</div>', unsafe_allow_html=True)


def _graph_for_context(cortex, context: MissionPlayerContext, data: dict):
    if context.entity_id is None:
        return None
    relationships = cortex.knowledge.get_current_relationships()
    signals = data.get("signals", [])
    strongest = max(
        signals,
        key=lambda signal: abs(float(signal.get("value", 0.0))),
        default=None,
    )
    source_impact = float(strongest.get("value", 0.0)) if strongest else 0.0
    propagation = []
    if source_impact:
        candidates = cortex.propagation_planner.plan(
            source_entity_id=context.entity_id,
            max_depth=2,
            source_impact_score=source_impact,
        )
        propagation = build_propagation_rows(candidates, source_impact)
    return build_explorer_graph(
        context.entity_id,
        relationships,
        max_depth=2,
        max_neighbors=12,
        impact_by_entity={row.entity_id: row.projected_impact for row in propagation},
        weight_by_entity={row.entity_id: row.propagation_weight for row in propagation},
        hops_by_entity={row.entity_id: row.hop_count for row in propagation},
        path_by_entity={row.entity_id: row.reason for row in propagation},
        source_impact=source_impact if strongest else None,
        seed_headline=strongest.get("headline", "Signal") if strongest else None,
    )


def render_mission_control(
    *,
    cortex,
    dashboard,
    scores: Mapping[tuple[str, str], dict],
    player_count: int,
    scored_player_count: int,
    passing_tests: int,
) -> None:
    """Render the synchronized Cortex operations console."""
    _inject_styles()
    st.markdown('<div class="mc-kicker">Cortex Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="mc-title">Mission Control</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mc-subtitle">Select one player context to synchronize live activity, graph propagation, and recommendation intelligence.</div>',
        unsafe_allow_html=True,
    )

    relationships = cortex.knowledge.get_current_relationships()
    contexts = build_player_contexts(scores, relationships)
    default_context = select_default_context(contexts)
    activity_service = ActivityFeedService(cortex.event_bus)

    selected_context = None
    if default_context is not None:
        labels = [f"{item.player} · {item.team}" for item in contexts]
        selected_label = st.selectbox(
            "Mission Control player context",
            labels,
            index=contexts.index(default_context),
            key="mission_control_player",
        )
        selected_context = contexts[labels.index(selected_label)]
        st.markdown(
            f'<div class="mc-context"><div class="mc-context-name">{selected_context.player} · {selected_context.team}</div>'
            f'<div class="mc-context-meta">Cortex score {selected_context.score:+.2f} · '
            f'{selected_context.signal_count} signals · '
            f'{"Graph connected" if selected_context.entity_id else "No graph entity"}</div></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([.92, 1.08])
    with left:
        st.markdown('<div class="mc-panel-title">Synchronized Activity</div>', unsafe_allow_html=True)
        groups = (
            activity_service.by_player(selected_context.player, limit=8)
            if selected_context
            else activity_service.latest(limit=8)
        )
        render_activity_feed(
            groups,
            empty_message=(
                "No Cortex activity is recorded for this player in the current session."
                if selected_context
                else "No Cortex events have been processed in this session yet."
            ),
        )
        st.markdown('<div class="mc-panel-title">Recommendation Center</div>', unsafe_allow_html=True)
        render_player_card(dashboard.top_buy, title="Top Buy")
        render_player_card(dashboard.top_watch, title="Watch List")
        render_player_card(dashboard.top_risk, title="Highest Risk")

    with right:
        st.markdown('<div class="mc-panel-title">Intelligence-Aware Graph</div>', unsafe_allow_html=True)
        if selected_context is None:
            st.info("No scored player context is available.")
        else:
            data = scores[(selected_context.player, selected_context.team)]
            graph = _graph_for_context(cortex, selected_context, data)
            if graph is None:
                st.info("This player is not currently represented in the Cortex relationship graph.")
            else:
                render_knowledge_graph(graph)

    st.divider()
    st.markdown('<div class="mc-panel-title">Operational Snapshot</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ranked Players", len(dashboard.rankings))
    m2.metric("Tracked Players", player_count)
    m3.metric("Scored Players", scored_player_count)
    m4.metric("Activity Stories", len(activity_service.latest(limit=25)))

    status = build_mission_control_status(
        event_count=len(cortex.get_event_history()),
        relationship_count=len(relationships),
        player_count=player_count,
        scored_player_count=scored_player_count,
        passing_tests=passing_tests,
    )
    _render_status_strip(status)
