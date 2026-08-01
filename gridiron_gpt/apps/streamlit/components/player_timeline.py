from datetime import datetime
import pandas as pd
import streamlit as st


def _format_timestamp(timestamp: str | None) -> str:
    if not timestamp:
        return "Unknown time"

    try:
        parsed = datetime.fromisoformat(timestamp)
        return parsed.strftime("%b %d, %Y %I:%M:%S %p")
    except ValueError:
        return timestamp


def _get_trend_label(score_change: float | None) -> str:
    if score_change is None:
        return "Initial Snapshot"

    if score_change > 0:
        return "📈 Rising"

    if score_change < 0:
        return "📉 Falling"

    return "➡ Stable"


def _render_recommendation_badge(recommendation: str | None) -> None:
    action = (recommendation or "WATCH").upper()

    if action in {"BUY", "START", "ADD"}:
        st.success(f"Recommendation: {action}")
    elif action in {"SELL", "DROP", "SIT"}:
        st.error(f"Recommendation: {action}")
    else:
        st.warning(f"Recommendation: {action}")


def render_player_timeline(result):
    """
    Render historical player scorecard snapshots supplied by Cortex.
    """
    st.markdown("### Player Timeline")
    st.caption(
        "Historical scorecard snapshots showing how player outlook "
        "changes as new evidence is processed."
    )

    if not result.scorecard_history:
        st.info("No scorecard history is available for this event.")
        return

    for player_id, history in result.scorecard_history.items():
        if not history:
            continue

        latest = history[-1]

        chart_rows = []

        for scorecard in history:
            chart_rows.append(
                {
                    "Time": _format_timestamp(scorecard.last_updated),
                    "Overall": scorecard.overall_score,
                    "Opportunity": scorecard.opportunity_score,
                    "Momentum": scorecard.momentum_score,
                    "Health": scorecard.health_score,
                    "Risk": scorecard.risk_score,
                }
            )

        chart_df = pd.DataFrame(chart_rows)

        st.markdown(
            f"#### {latest.player_name} "
            f"({latest.team or 'UNK'})"
        )
        st.markdown("##### Score Evolution")

        st.line_chart(
            chart_df.set_index("Time"),
            height=250,
        )

        reversed_history = list(reversed(history))

        for index, scorecard in enumerate(reversed_history):
            older_scorecard = (
                reversed_history[index + 1]
                if index + 1 < len(reversed_history)
                else None
            )

            score_change = (
                scorecard.overall_score
                - older_scorecard.overall_score
                if older_scorecard is not None
                else None
            )

            timestamp = _format_timestamp(
                scorecard.last_updated
            )

            trend_label = _get_trend_label(
                score_change
            )

            expanded = index == 0

            with st.expander(
                f"{timestamp} · {trend_label}",
                expanded=expanded,
            ):
                st.caption(f"Player ID: {player_id}")

                overall_col, trend_col = st.columns(2)

                with overall_col:
                    if score_change is None:
                        st.metric(
                            "Overall Score",
                            f"{scorecard.overall_score:.1f}",
                        )
                    else:
                        st.metric(
                            "Overall Score",
                            f"{scorecard.overall_score:.1f}",
                            delta=f"{score_change:+.1f}",
                        )

                with trend_col:
                    st.metric(
                        "Trend",
                        trend_label,
                    )

                score_cols = st.columns(4)

                with score_cols[0]:
                    st.metric(
                        "Opportunity",
                        f"{scorecard.opportunity_score:.1f}",
                    )

                with score_cols[1]:
                    st.metric(
                        "Momentum",
                        f"{scorecard.momentum_score:.1f}",
                    )

                with score_cols[2]:
                    st.metric(
                        "Health",
                        f"{scorecard.health_score:.1f}",
                    )

                with score_cols[3]:
                    st.metric(
                        "Risk",
                        f"{scorecard.risk_score:.1f}",
                    )

                recommendation = getattr(
                    scorecard,
                    "recommendation",
                    None,
                )

                _render_recommendation_badge(
                    recommendation
                )
