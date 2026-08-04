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


def _impact_style(impact: float | None) -> tuple[str, str, str]:
    if impact is None:
        return "#0d2115", "#48c978", "neutral"
    if impact > 0:
        return "#123b24", "#79ff9f", "positive"
    if impact < 0:
        return "#3d141a", "#ff6b78", "negative"
    return "#1c2420", "#a3b0a8", "neutral"


def _edge_style(impact: float | None, confidence: float) -> tuple[str, str]:
    opacity = max(0.32, min(1.0, confidence))
    if impact is not None and impact > 0:
        return f"rgba(105,240,145,{opacity:.2f})", "arrow-positive"
    if impact is not None and impact < 0:
        return f"rgba(255,107,120,{opacity:.2f})", "arrow-negative"
    return f"rgba(118,145,128,{opacity:.2f})", "arrow-neutral"


def render_knowledge_graph(graph: ExplorerGraph) -> None:
    """Render a clickable, propagation-aware Cortex knowledge graph."""
    st.markdown("### Knowledge Graph")
    if len(graph.nodes) <= 1 or not graph.edges:
        st.info("No active graph connections are available for this player.")
        return

    if graph.seed_headline and graph.source_impact is not None:
        st.caption(
            f"Propagation seed: {graph.seed_headline} "
            f"({graph.source_impact:+.2f})"
        )

    positions = _node_positions(graph)

    edge_markup: list[str] = []
    for edge in graph.edges:
        if edge.source_id not in positions or edge.target_id not in positions:
            continue
        x1, y1 = positions[edge.source_id]
        x2, y2 = positions[edge.target_id]
        width = 1.5 + max(0.0, edge.strength) * 3.2
        label_x = (x1 + x2) / 2
        label_y = (y1 + y2) / 2
        stroke, marker = _edge_style(edge.projected_impact, edge.confidence)
        impact_suffix = (
            f" {edge.projected_impact:+.2f}"
            if edge.projected_impact is not None
            else ""
        )
        edge_title = escape(
            f"{edge.relationship_type}; strength {edge.strength:.2f}; "
            f"confidence {edge.confidence:.0%}"
            + (
                f"; projected impact {edge.projected_impact:+.3f}"
                if edge.projected_impact is not None
                else ""
            )
        )
        edge_markup.append(
            f'<g><title>{edge_title}</title>'
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width:.2f}" marker-end="url(#{marker})" />'
            f'<rect x="{label_x - 66:.1f}" y="{label_y - 13:.1f}" width="132" height="22" rx="7" fill="#07130b" opacity="0.95" />'
            f'<text x="{label_x:.1f}" y="{label_y + 2:.1f}" text-anchor="middle" fill="#c3cec7" font-size="10.5">'
            f'{escape(edge.relationship_type)}{impact_suffix}</text></g>'
        )

    node_markup: list[str] = []
    for node in graph.nodes:
        if node.entity_id not in positions:
            continue
        x, y = positions[node.entity_id]
        fill, stroke, impact_label = _impact_style(node.projected_impact)
        magnitude = abs(node.projected_impact or 0.0)
        radius = 62 if node.is_root else 46 + min(magnitude, 1.0) * 16
        if node.is_root:
            fill = "#1b7f43"
            stroke = "#b0ffc6"
        label = escape(node.name)
        team = escape(node.team or "")
        href = f"?page=Explorer&player={quote(node.name)}"
        impact_text = (
            f"{node.projected_impact:+.2f}"
            if node.projected_impact is not None
            else ""
        )
        tooltip = escape(
            f"{node.name} ({node.team or 'UNK'})"
            + (
                f"; {impact_label} projected impact {node.projected_impact:+.3f}"
                if node.projected_impact is not None
                else "; no propagated impact on current seed"
            )
            + (
                f"; {node.hop_count} hop(s)"
                if node.hop_count is not None
                else ""
            )
        )
        node_markup.append(
            f'<a href="{href}" target="_top"><g><title>{tooltip}</title>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.6" />'
            f'<text x="{x:.1f}" y="{y - 7:.1f}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700">{label}</text>'
            f'<text x="{x:.1f}" y="{y + 11:.1f}" text-anchor="middle" fill="#b6c3bb" font-size="10.5">{team}</text>'
            + (
                f'<text x="{x:.1f}" y="{y + 29:.1f}" text-anchor="middle" fill="{stroke}" font-size="11.5" font-weight="700">{impact_text}</text>'
                if impact_text
                else ""
            )
            + '</g></a>'
        )

    st.markdown(
        f"""
        <div style="overflow-x:auto;border:1px solid rgba(82,214,124,.18);border-radius:12px;background:#050906;padding:.4rem;">
        <svg viewBox="0 0 900 520" width="100%" style="min-width:720px;max-height:560px;">
          <defs>
            <marker id="arrow-positive" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#69f091" /></marker>
            <marker id="arrow-negative" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#ff6b78" /></marker>
            <marker id="arrow-neutral" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#768e80" /></marker>
          </defs>
          {''.join(edge_markup)}
          {''.join(node_markup)}
        </svg>
        </div>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;color:#91a098;font-size:.78rem;margin-top:.45rem;">
          <span><b style="color:#79ff9f">● Positive</b></span>
          <span><b style="color:#ff6b78">● Negative</b></span>
          <span><b style="color:#a3b0a8">● No current propagated effect</b></span>
          <span>Node size = impact magnitude</span>
          <span>Edge width = relationship strength</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    inspectable = [
        node
        for node in graph.nodes
        if not node.is_root and node.evidence_path
    ]
    if inspectable:
        st.markdown("#### Evidence Path Inspection")
        for node in sorted(
            inspectable,
            key=lambda item: abs(item.projected_impact or 0.0),
            reverse=True,
        ):
            team = f" ({node.team})" if node.team else ""
            impact = node.projected_impact or 0.0
            with st.expander(f"{node.name}{team} · {impact:+.3f}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Projected Impact", f"{impact:+.3f}")
                c2.metric("Propagation Weight", f"{(node.propagation_weight or 0.0):+.3f}")
                c3.metric("Hops", node.hop_count if node.hop_count is not None else "—")
                st.code(node.evidence_path, language=None)
