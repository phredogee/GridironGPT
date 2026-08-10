from __future__ import annotations

import pandas as pd
import streamlit as st

from gridiron_gpt.intelligence.visualization_models import (
    build_cortex_timeline,
    build_signal_breakdown,
    confidence_components,
    position_rankings,
    recommendation_distribution,
    team_momentum,
)


def _bar_frame(rows, *, label_name: str, value_name: str) -> pd.DataFrame:
    return pd.DataFrame(
        [{label_name: row.label, value_name: row.value} for row in rows]
    ).set_index(label_name)


def render_confidence_panel(confidence: int, signals: list[dict]) -> None:
    components = confidence_components(signals)
    st.metric("Confidence", f"{confidence}%")
    st.progress(max(0.0, min(1.0, confidence / 100)))
    col1, col2, col3 = st.columns(3)
    col1.metric("Signal agreement", f"{components['agreement'] * 100:.0f}%")
    col2.metric("Positive share", f"{components['positive_share'] * 100:.0f}%")
    col3.metric("Negative share", f"{components['negative_share'] * 100:.0f}%")


def render_signal_breakdown(signals: list[dict]) -> None:
    rows = build_signal_breakdown(signals)
    st.markdown("### Signal Impact")
    if not rows:
        st.info("No scored signals are available yet.")
        return
    frame = _bar_frame(rows, label_name="Signal", value_name="Impact")
    st.bar_chart(frame, horizontal=True, use_container_width=True)


def render_cortex_timeline(signals: list[dict]) -> None:
    rows = build_cortex_timeline(signals)
    st.markdown("### Cortex Timeline")
    if not rows:
        st.info("No timeline events are available yet.")
        return

    frame = pd.DataFrame(
        [
            {
                "Date": row.label,
                "Cortex score": row.cumulative_score,
            }
            for row in rows
        ]
    ).set_index("Date")
    st.line_chart(frame, use_container_width=True)

    for row in reversed(rows):
        marker = "Positive" if row.value > 0 else "Negative" if row.value < 0 else "Neutral"
        with st.expander(f"{row.label} · {marker} · {row.value:+.2f}"):
            st.write(row.headline)
            st.caption(f"{row.source} · Running score {row.cumulative_score:+.2f}")


def render_platform_charts(scores: dict, positions: dict[str, str]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Recommendation Distribution")
        frame = _bar_frame(
            recommendation_distribution(scores),
            label_name="Recommendation",
            value_name="Players",
        )
        st.bar_chart(frame, use_container_width=True)

    with col2:
        st.markdown("### Team Momentum")
        rows = team_momentum(scores)[:12]
        if rows:
            frame = _bar_frame(rows, label_name="Team", value_name="Score")
            st.bar_chart(frame, horizontal=True, use_container_width=True)
        else:
            st.info("No team momentum is available yet.")

    st.markdown("### Position Rankings")
    grouped = position_rankings(scores, positions)
    tabs = st.tabs([position for position in ("QB", "RB", "WR", "TE", "DST")])
    for tab, position in zip(tabs, ("QB", "RB", "WR", "TE", "DST")):
        with tab:
            rows = grouped.get(position, [])[:10]
            if rows:
                frame = _bar_frame(rows, label_name="Player", value_name="Score")
                st.bar_chart(frame, horizontal=True, use_container_width=True)
            else:
                st.info(f"No scored {position} players are available yet.")
