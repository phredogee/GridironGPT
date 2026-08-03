from __future__ import annotations

import math
from html import escape
from urllib.parse import quote

import streamlit as st

from gridiron_gpt.intelligence.explorer_graph import ExplorerGraph


def _node_positions(graph: ExplorerGraph) -> dict[str, tuple[float, float]]:
    width = 900.0
    height = 520.0
    center = (width / 2, height / 2)
    positions = {graph.root_id: center}
    neighbors = [node for node in graph.nodes if not node.is_root]
    if not neighbors:
        return positions

    radius_x = 330.0
    radius_y = 185.0
    for index, node in enumerate(neighbors):
        angle = (2 * math.pi * index / len(neighbors)) - math.pi / 2
        positions[node.entity_id] = (
            center[0] + radius_x * math.cos(angle),
            center[1] + radius_y * math.sin(angle),
        )
    return positions


def render_knowledge_graph(graph: ExplorerGraph) -> None:
    """Render a clickable one-hop Cortex relationship graph."""
    st.markdown("### Knowledge Graph")
    if len(graph.nodes) <= 1 or not graph.edges:
        st.info("No active graph connections are available for this player.")
        return

    positions = _node_positions(graph)
    nodes_by_id = {node.entity_id: node for node in graph.nodes}

    edge_markup: list[str] = []
    for edge in graph.edges:
        if edge.source_id not in positions or edge.target_id not in positions:
            continue
        x1, y1 = positions[edge.source_id]
        x2, y2 = positions[edge.target_id]
        opacity = max(0.3, min(1.0, edge.confidence))
        width = 1.5 + max(0.0, edge.strength) * 3.0
        label_x = (x1 + x2) / 2
        label_y = (y1 + y2) / 2
        edge_markup.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="rgba(105,240,145,{opacity:.2f})" stroke-width="{width:.2f}" marker-end="url(#arrow)" />'
            f'<rect x="{label_x - 58:.1f}" y="{label_y - 13:.1f}" width="116" height="22" rx="7" fill="#07130b" opacity="0.94" />'
            f'<text x="{label_x:.1f}" y="{label_y + 2:.1f}" text-anchor="middle" fill="#b9c7be" font-size="11">{escape(edge.relationship_type)}</text>'
        )

    node_markup: list[str] = []
    for node in graph.nodes:
        if node.entity_id not in positions:
            continue
        x, y = positions[node.entity_id]
        root = node.is_root
        radius = 61 if root else 48
        fill = "#1b7f43" if root else "#0d2115"
        stroke = "#79ff9f" if root else "#48c978"
        label = escape(node.name)
        team = escape(node.team or "")
        href = f"?page=Explorer&player={quote(node.name)}"
        node_markup.append(
            f'<a href="{href}" target="_top">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" />'
            f'<text x="{x:.1f}" y="{y - 3:.1f}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700">{label}</text>'
            f'<text x="{x:.1f}" y="{y + 16:.1f}" text-anchor="middle" fill="#a9bbb0" font-size="11">{team}</text>'
            '</a>'
        )

    st.markdown(
        f"""
        <div style="overflow-x:auto;border:1px solid rgba(82,214,124,.18);border-radius:12px;background:#050906;padding:.4rem;">
        <svg viewBox="0 0 900 520" width="100%" style="min-width:720px;max-height:560px;">
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L8,3 z" fill="#69f091" />
            </marker>
          </defs>
          {''.join(edge_markup)}
          {''.join(node_markup)}
        </svg>
        </div>
        <div style="color:#91a098;font-size:.78rem;margin-top:.35rem;">Click a connected player to recenter Cortex Explorer on that node. Edge thickness reflects relationship strength; brightness reflects confidence.</div>
        """,
        unsafe_allow_html=True,
    )
