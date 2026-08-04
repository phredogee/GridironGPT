from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from urllib.parse import quote

import streamlit as st

from gridiron_cortex.activity.activity_models import (
    ActivityCard,
    ActivityGroup,
    ActivitySeverity,
)


_SEVERITY_COLORS = {
    ActivitySeverity.INFO: "#74b9ff",
    ActivitySeverity.POSITIVE: "#79ff9f",
    ActivitySeverity.WARNING: "#ffd166",
    ActivitySeverity.NEGATIVE: "#ff6b78",
}


def relative_time(
    timestamp: datetime,
    *,
    now: datetime | None = None,
) -> str:
    """Return a compact user-facing age for a timezone-aware timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    seconds = max(0, int((current - timestamp).total_seconds()))
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 7:
        return f"{days}d ago"
    return timestamp.astimezone(timezone.utc).strftime("%b %d, %Y")


def summarize_activity_group(group: ActivityGroup) -> str:
    """Build the compact label used for an expandable activity story."""
    source = f" · {group.source}" if group.source else ""
    entity = f" · {group.entity_name}" if group.entity_name else ""
    return f"{group.headline}{entity}{source} · {group.event_count} events"


def _render_card(card: ActivityCard) -> None:
    color = _SEVERITY_COLORS[card.severity]
    entity = f" · {escape(card.entity_name)}" if card.entity_name else ""
    source = f" · {escape(card.source)}" if card.source else ""
    st.markdown(
        f"""
        <div style="border-left:3px solid {color};padding:.28rem .2rem .42rem .72rem;margin:.28rem 0 .55rem;">
          <div style="font-size:.92rem;font-weight:700;color:#f4f8f5;">
            {escape(card.icon)} {escape(card.title)}
          </div>
          <div style="font-size:.78rem;color:#9facA4;margin-top:.12rem;">
            {escape(card.subtitle)}{entity}{source} · {relative_time(card.timestamp)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if card.entity_name:
        st.markdown(
            f"[Open {card.entity_name} in Cortex Explorer]"
            f"(?page=Explorer&player={quote(card.entity_name)})"
        )
    if card.details:
        with st.expander("Event details", expanded=False):
            st.json(dict(card.details))
            st.caption(
                f"Correlation: {card.correlation_id} · Event: {card.event_id}"
            )


def render_activity_feed(
    groups: tuple[ActivityGroup, ...] | list[ActivityGroup],
    *,
    title: str = "Live Cortex Activity",
    empty_message: str = "No Cortex processing events have been recorded in this session yet.",
) -> None:
    """Render correlated Cortex events as an expandable activity timeline."""
    st.markdown(f"### {title}")
    st.caption("Each entry groups the complete reasoning trail for one Cortex run.")

    if not groups:
        st.info(empty_message)
        return

    for index, group in enumerate(groups):
        label = summarize_activity_group(group)
        with st.expander(label, expanded=index == 0):
            st.caption(
                f"Latest activity {relative_time(group.latest_timestamp)} · "
                f"Correlation {group.correlation_id}"
            )
            for card in group.cards:
                _render_card(card)
