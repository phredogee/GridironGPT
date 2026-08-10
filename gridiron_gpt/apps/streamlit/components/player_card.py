from __future__ import annotations

from html import escape

import streamlit as st

from apps.streamlit.view_models.dashboard import DashboardPlayer


def render_player_card(
    player: DashboardPlayer | None,
    *,
    title: str,
) -> None:
    """
    Render a Cortex player recommendation card.

    Parameters
    ----------
    player
        Dashboard player to display. If None, an empty card is shown.

    title
        Section title such as:
            Top Buy
            Watch List
            Highest Risk
    """

    if player is None:
        st.info(f"{title}: No player available.")
        return

    st.markdown(
        f"""
<div style="
padding:18px;
border-radius:14px;
background:#20232d;
border:1px solid rgba(255,255,255,.08);
margin-bottom:1rem;
">

<div style="
font-size:.80rem;
font-weight:700;
color:#7dd3fc;
text-transform:uppercase;
margin-bottom:.5rem;
">
{escape(title)}
</div>

<div style="
font-size:1.25rem;
font-weight:700;
color:white;
">
{escape(player.name)}
</div>

<div style="
color:#9ca3af;
margin-bottom:1rem;
">
{escape(player.team)}
</div>

<hr style="border-color:#2f3440;">

<div style="display:flex;justify-content:space-between;">
<span>Recommendation</span>
<strong>{escape(player.recommendation)}</strong>
</div>

<div style="display:flex;justify-content:space-between;">
<span>Score</span>
<strong>{player.score:.1f}</strong>
</div>

<div style="display:flex;justify-content:space-between;">
<span>Confidence</span>
<strong>{player.confidence:.0f}%</strong>
</div>

</div>
""",
        unsafe_allow_html=True,
    )
