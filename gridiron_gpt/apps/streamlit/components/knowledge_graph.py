from __future__ import annotations

import math
from collections import defaultdict
from html import escape
from urllib.parse import quote

import streamlit as st

from gridiron_gpt.intelligence.explorer_graph import ExplorerGraph


_GRAPH_WIDTH = 1400.0
_GRAPH_HEIGHT = 900.0
_RING_RADII = {
    1: (315.0, 225.0),
    2: (590.0, 365.0),
    3: (650.0, 405.0),
}


def _ring_radius(depth: int) -> tuple[float, float]:
    if depth in _RING_RADII:
        return _RING_RADII[depth]
    extra = depth - max(_RING_RADII)
    base_x, base_y = _RING_RADII[max(_RING_RADII)]
    return min(675.0, base_x + extra * 35.0), min(420.0, base_y + extra * 22.0)


def _node_positions(graph: ExplorerGraph) -> dict[str, tuple[float, float]]:
    """Place the seed at center and each graph depth on a deterministic ring."""
    center = (_GRAPH_WIDTH / 2, _GRAPH_HEIGHT / 2)
    positions = {graph.root_id: center}
    by_depth: dict[int, list] = defaultdict(list)
    for node in graph.nodes:
        if not node.is_root:
            by_depth[max(1, node.depth)].append(node)

    for depth, nodes in sorted(by_depth.items()):
        nodes = sorted(nodes, key=lambda item: (item.team or "", item.name, item.entity_id))
        radius_x, radius_y = _ring_radius(depth)
        count = max(1, len(nodes))
        offset = -math.pi / 2 + (math.pi / count if depth % 2 == 0 else 0.0)
        for index, node in enumerate(nodes):
            angle = (2 * math.pi * index / count) + offset
            positions[node.entity_id] = (
                center[0] + radius_x * math.cos(angle),
                center[1] + radius_y * math.sin(angle),
            )
    return positions


def _curve_control_point(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    direction: int,
) -> tuple[float, float]:
    """Return a modest perpendicular bend that separates crossing edges."""
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    distance = max(1.0, math.hypot(dx, dy))
    bend = min(54.0, max(20.0, distance * 0.075)) * direction
    return mid_x - (dy / distance) * bend, mid_y + (dx / distance) * bend


def _quadratic_point(
    x1: float,
    y1: float,
    cx: float,
    cy: float,
    x2: float,
    y2: float,
    t: float = 0.5,
) -> tuple[float, float]:
    inverse = 1.0 - t
    return (
        inverse * inverse * x1 + 2 * inverse * t * cx + t * t * x2,
        inverse * inverse * y1 + 2 * inverse * t * cy + t * t * y2,
    )


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
    """Render a clickable, multi-hop, propagation-aware radial graph."""
    st.markdown("### Knowledge Graph")
    if len(graph.nodes) <= 1 or not graph.edges:
        st.info("No graph connections match the current filters.")
        return

    if graph.seed_headline and graph.source_impact is not None:
        st.caption(
            f"Propagation seed: {graph.seed_headline} "
            f"({graph.source_impact:+.2f}) · depth {graph.max_depth}"
        )

    positions = _node_positions(graph)

    ring_markup = []
    for depth in sorted({max(1, node.depth) for node in graph.nodes if not node.is_root}):
        radius_x, radius_y = _ring_radius(depth)
        ring_markup.append(
            f'<ellipse cx="{_GRAPH_WIDTH / 2:.1f}" cy="{_GRAPH_HEIGHT / 2:.1f}" '
            f'rx="{radius_x:.1f}" ry="{radius_y:.1f}" fill="none" '
            f'stroke="rgba(90,190,120,.13)" stroke-width="1.2" stroke-dasharray="7 9" />'
            f'<text x="{_GRAPH_WIDTH / 2 + radius_x - 42:.1f}" y="{_GRAPH_HEIGHT / 2 - 8:.1f}" '
            f'fill="rgba(145,180,156,.55)" font-size="11">hop {depth}</text>'
        )

    edge_markup: list[str] = []
    for index, edge in enumerate(graph.edges):
        if edge.source_id not in positions or edge.target_id not in positions:
            continue
        x1, y1 = positions[edge.source_id]
        x2, y2 = positions[edge.target_id]
        direction = -1 if index % 2 else 1
        cx, cy = _curve_control_point(x1, y1, x2, y2, direction=direction)
        label_x, label_y = _quadratic_point(x1, y1, cx, cy, x2, y2)
        width = 1.4 + max(0.0, edge.strength) * 3.0
        stroke, marker = _edge_style(edge.projected_impact, edge.confidence)
        impact_suffix = f" {edge.projected_impact:+.2f}" if edge.projected_impact is not None else ""
        edge_title = escape(
            f"{edge.relationship_type}; strength {edge.strength:.2f}; confidence {edge.confidence:.0%}"
            + (f"; projected impact {edge.projected_impact:+.3f}" if edge.projected_impact is not None else "")
        )
        edge_markup.append(
            f'<g><title>{edge_title}</title>'
            f'<path d="M {x1:.1f},{y1:.1f} Q {cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{stroke}" stroke-width="{width:.2f}" marker-end="url(#{marker})" />'
            f'<rect x="{label_x - 67:.1f}" y="{label_y - 12:.1f}" width="134" height="21" rx="7" fill="#07130b" opacity="0.94" />'
            f'<text x="{label_x:.1f}" y="{label_y + 2:.1f}" text-anchor="middle" fill="#c3cec7" font-size="10">'
            f'{escape(edge.relationship_type)}{impact_suffix}</text></g>'
        )

    node_markup: list[str] = []
    for node in graph.nodes:
        if node.entity_id not in positions:
            continue
        x, y = positions[node.entity_id]
        fill, stroke, impact_label = _impact_style(node.projected_impact)
        magnitude = abs(node.projected_impact or 0.0)
        radius = 62 if node.is_root else 43 + min(magnitude, 1.0) * 13
        if node.depth >= 2 and not node.is_root:
            radius = max(36, radius - 4)
        if node.is_root:
            fill, stroke = "#1b7f43", "#b0ffc6"
        label = escape(node.name)
        team = escape(node.team or "")
        href = f"?page=Explorer&player={quote(node.name)}"
        impact_text = f"{node.projected_impact:+.2f}" if node.projected_impact is not None else ""
        tooltip = escape(
            f"{node.name} ({node.team or 'UNK'}); graph depth {node.depth}"
            + (f"; {impact_label} projected impact {node.projected_impact:+.3f}" if node.projected_impact is not None else "; no propagated impact on current seed")
            + (f"; {node.hop_count} propagation hop(s)" if node.hop_count is not None else "")
        )
        node_markup.append(
            f'<a href="{href}" target="_top"><g><title>{tooltip}</title>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" />'
            f'<text x="{x:.1f}" y="{y - 8:.1f}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">{label}</text>'
            f'<text x="{x:.1f}" y="{y + 8:.1f}" text-anchor="middle" fill="#b6c3bb" font-size="10">{team}</text>'
            f'<text x="{x:.1f}" y="{y + 23:.1f}" text-anchor="middle" fill="#85968b" font-size="9.5">hop {node.depth}</text>'
            + (f'<text x="{x:.1f}" y="{y + 37:.1f}" text-anchor="middle" fill="{stroke}" font-size="10.5" font-weight="700">{impact_text}</text>' if impact_text else "")
            + '</g></a>'
        )

    st.markdown(
        f"""
        <div style="overflow:auto;border:1px solid rgba(82,214,124,.18);border-radius:12px;background:#050906;padding:.4rem;">
        <svg viewBox="0 0 {_GRAPH_WIDTH:.0f} {_GRAPH_HEIGHT:.0f}" width="100%" style="min-width:1050px;max-height:820px;">
          <defs>
            <marker id="arrow-positive" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#69f091" /></marker>
            <marker id="arrow-negative" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#ff6b78" /></marker>
            <marker id="arrow-neutral" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L8,3 z" fill="#768e80" /></marker>
          </defs>
          {''.join(ring_markup)}
          {''.join(edge_markup)}
          {''.join(node_markup)}
        </svg>
        </div>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;color:#91a098;font-size:.78rem;margin-top:.45rem;">
          <span><b style="color:#79ff9f">● Positive</b></span><span><b style="color:#ff6b78">● Negative</b></span>
          <span><b style="color:#a3b0a8">● No current propagated effect</b></span><span>Dashed rings = graph hops</span>
          <span>Node size = impact magnitude</span><span>Edge width = relationship strength</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    inspectable = [node for node in graph.nodes if not node.is_root and node.evidence_path]
    if inspectable:
        st.markdown("#### Evidence Path Inspection")
        for node in sorted(inspectable, key=lambda item: abs(item.projected_impact or 0.0), reverse=True):
            team = f" ({node.team})" if node.team else ""
            impact = node.projected_impact or 0.0
            with st.expander(f"{node.name}{team} · {impact:+.3f}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Projected Impact", f"{impact:+.3f}")
                c2.metric("Propagation Weight", f"{(node.propagation_weight or 0.0):+.3f}")
                c3.metric("Hops", node.hop_count if node.hop_count is not None else "—")
                st.code(node.evidence_path, language=None)
