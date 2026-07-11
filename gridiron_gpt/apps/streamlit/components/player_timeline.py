from datetime import datetime

import streamlit as st


def _format_timestamp(timestamp: str | None) -> str:
    if not timestamp:
        return "Unknown time"

    try:
        parsed = datetime.fromisoformat(timestamp)
        return parsed.strftime("%b %d, %Y %I:%M:%S %p")
    except ValueError:
        return timestamp


def render_player_timeline(result):
    """
    Render scorecard history supplied by the Cortex engine.
    """
    st.markdown("### Player Timeline")
    st.caption("Historical scorecard snapshots stored by Cortex.")

    if not result.scorecard_history:
        st.info("No scorecard history is available for this event.")
        return

    for player_id, history in result.scorecard_history.items():
        if not history:
            continue

        latest = history[-1]

        st.write(
            f"**{latest.player_name}** "
            f"({latest.team or 'UNK'})"
        )

        previous_score = None

        reversed_history = list(reversed(history))

        for index, scorecard in enumerate(reversed_history):
            older_scorecard = (
                reversed_history[index + 1]
                if index + 1 < len(reversed_history)
                else None
            )

            score_change = (
                scorecard.overall_score - older_scorecard.overall_score
                if older_scorecard is not None
                else None
            )

            timestamp = _format_timestamp(scorecard.last_updated)

            with st.container(border=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**{timestamp}**")
                    st.caption(f"Player ID: {player_id}")

                with col2:
                    if score_change is None:
                        st.metric(
                            "Overall",
                            f"{scorecard.overall_score:.1f}",
                        )
                    else:
                        st.metric(
                            "Overall",
                            f"{scorecard.overall_score:.1f}",
                            delta=f"{score_change:+.1f}",
                        )

            previous_score = scorecard.overall_score
