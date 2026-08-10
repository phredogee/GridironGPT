from __future__ import annotations

from collections.abc import Sequence
from html import escape

import streamlit as st

from apps.streamlit.view_models.dashboard import DashboardPlayer


def _badge_class(recommendation: str) -> str:
    """Return the CSS class for a recommendation badge."""

    normalized = recommendation.strip().upper()

    if normalized == "BUY":
        return "dashboard-badge-buy"

    if normalized in {"WATCH", "HOLD", "MONITOR"}:
        return "dashboard-badge-watch"

    if normalized in {"RISK", "SELL", "AVOID"}:
        return "dashboard-badge-risk"

    return "dashboard-badge-neutral"


def _render_badge(recommendation: str) -> None:
    """Render a recommendation badge."""

    safe_recommendation = escape(recommendation)
    badge_class = _badge_class(recommendation)

    st.markdown(
        (
            f'<span class="dashboard-badge {badge_class}">'
            f"{safe_recommendation}"
            "</span>"
        ),
        unsafe_allow_html=True,
    )


def _format_score(score: float) -> str:
    """Format a signed player score."""

    return f"{score:+.1f}"


def _format_confidence(confidence: float) -> str:
    """Format a confidence percentage."""

    return f"{confidence:.0f}%"


def _render_ranking_row(
    *,
    rank: int,
    player: DashboardPlayer,
) -> None:
    """Render one player ranking row."""

    with st.container(border=True):
        columns = st.columns(
            [0.5, 3.2, 1.4, 1.1, 1.3],
            vertical_alignment="center",
        )

        with columns[0]:
            st.markdown(f"**{rank:02d}**")

        with columns[1]:
            st.markdown(
                (
                    '<div class="dashboard-ranking-name">'
                    f"{escape(player.name)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="dashboard-ranking-team">'
                    f"{escape(player.team)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with columns[2]:
            _render_badge(player.recommendation)

        with columns[3]:
            st.markdown(
                (
                    '<div class="dashboard-ranking-value">'
                    f"{_format_score(player.score)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with columns[4]:
            st.markdown(
                (
                    '<div class="dashboard-ranking-value">'
                    f"{_format_confidence(player.confidence)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_rankings_table(
    rankings: Sequence[DashboardPlayer],
) -> None:
    """Render a ranked collection of Dashboard players."""

    if not rankings:
        st.info("No scored players are currently available.")
        return

    header_columns = st.columns(
        [0.5, 3.2, 1.4, 1.1, 1.3],
    )

    header_columns[0].caption("RANK")
    header_columns[1].caption("PLAYER")
    header_columns[2].caption("RATING")
    header_columns[3].caption("SCORE")
    header_columns[4].caption("CONFIDENCE")

    for rank, player in enumerate(rankings, start=1):
        _render_ranking_row(
            rank=rank,
            player=player,
        )
