from __future__ import annotations

import streamlit as st

from apps.streamlit.components.intelligence_charts import (
    render_confidence_panel,
    render_cortex_timeline,
    render_signal_breakdown,
)
from gridiron_gpt.intelligence.player_intelligence import build_player_intelligence


def _profile_values(intel: dict) -> tuple[tuple[str, int], ...]:
    signals = intel.get("recent_signals", [])
    positive = sum(max(float(signal.get("value", 0.0)), 0.0) for signal in signals)
    negative = sum(abs(min(float(signal.get("value", 0.0)), 0.0)) for signal in signals)
    total = positive + negative
    score = float(intel.get("score", 0.0))
    opportunity = min(100, int(50 + positive * 25))
    momentum = min(100, int(50 + max(score, 0.0) * 20))
    risk = min(100, int((negative / total) * 100)) if total else 0
    health = max(0, 100 - risk)
    upside = min(100, int((opportunity + momentum) / 2))
    return (
        ("Health", health),
        ("Opportunity", opportunity),
        ("Momentum", momentum),
        ("Risk", risk),
        ("Upside", upside),
    )


def _render_profile(intel: dict) -> None:
    st.markdown("### Cortex Profile")
    for label, value in _profile_values(intel):
        left, right = st.columns([5, 1])
        with left:
            st.caption(label)
            st.progress(value / 100)
        with right:
            st.metric(label="", value=f"{value}%")


def _render_direction(intel: dict) -> None:
    trend = intel.get("trend", {})
    momentum = intel.get("momentum", {})
    left, right = st.columns(2)
    with left:
        st.markdown("### Trend")
        if trend.get("status") == "ok":
            st.metric(
                "Score Change",
                f"{float(trend.get('change', 0.0)):+.2f}",
                delta=str(trend.get("direction", "stable")).upper(),
            )
            st.caption(
                f"Previous {float(trend.get('previous_score', 0.0)):+.2f} → "
                f"Current {float(trend.get('current_score', intel.get('score', 0.0))):+.2f}"
            )
        else:
            st.info("More score history is needed to establish a trend.")
    with right:
        st.markdown("### Trajectory")
        if momentum.get("status") == "ok":
            st.metric(
                "Momentum Score",
                f"{float(momentum.get('momentum_score', 0.0)):+.2f}",
                delta=str(momentum.get("direction", "stable")).upper(),
            )
        else:
            st.info("More score snapshots are needed to establish trajectory.")


def _render_evidence(signals: list[dict]) -> None:
    st.markdown("### Evidence Timeline")
    if not signals:
        st.info("No scored evidence is available for this player yet.")
        return
    for signal in reversed(signals):
        value = float(signal.get("value", 0.0))
        st.markdown(f"**{signal.get('headline', 'Signal')}**")
        st.caption(
            f"{signal.get('source', 'Unknown source')} · "
            f"{signal.get('impact', 'unknown')} · {value:+.2f}"
        )


def render_cortex_explorer(player_names: list[str]) -> None:
    """Render the unified Cortex player-intelligence dossier."""
    if not player_names:
        st.warning("No players are available in the current catalog.")
        return

    default_player = "Tank Dell" if "Tank Dell" in player_names else player_names[0]
    selected_player = st.selectbox(
        "Player",
        player_names,
        index=player_names.index(default_player),
        key="cortex_explorer_player",
    )
    intel = build_player_intelligence(selected_player)
    if intel.get("status") != "ok":
        st.warning(f"No scored intelligence found for {selected_player}.")
        return

    signals = intel.get("recent_signals", [])
    st.markdown(f"## {intel['player']} · {intel['team']}")
    st.caption("Unified Cortex intelligence dossier")

    rec_col, score_col, confidence_col, evidence_col = st.columns(4)
    rec_col.metric("Recommendation", intel["recommendation"])
    score_col.metric("Cortex Score", f"{float(intel['score']):+.2f}")
    confidence_col.metric("Confidence", f"{intel['confidence']}%")
    evidence_col.metric("Recent Evidence", len(signals))

    st.divider()
    left, right = st.columns([1, 1])
    with left:
        _render_profile(intel)
    with right:
        st.markdown("### Confidence & Agreement")
        render_confidence_panel(intel["confidence"], signals)
        render_signal_breakdown(signals)

    st.divider()
    _render_direction(intel)
    st.divider()
    render_cortex_timeline(signals)
    st.divider()
    _render_evidence(signals)
