import streamlit as st


def render_propagation_panel(result):
    """Render direct and propagated Cortex impacts."""

    st.markdown("### Propagation")
    st.caption(
        "Shows how a direct player signal travels through "
        "the Cortex relationship graph."
    )

    if not result.impacts:
        st.info("No impacts were generated.")
        return

    direct_impacts = [
        impact
        for impact in result.impacts
        if impact.impact_type == "direct"
    ]

    propagated_impacts = [
        impact
        for impact in result.impacts
        if impact.impact_type == "propagated"
    ]

    if direct_impacts:
        st.markdown("#### Direct Impact")

        for impact in direct_impacts:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Entity",
                    impact.entity_name,
                )

                col2.metric(
                    "Team",
                    impact.team or "UNK",
                )

                col3.metric(
                    "Impact",
                    f"{impact.impact_score:+.3f}",
                )

                if impact.reason:
                    st.caption(impact.reason)

    st.markdown("#### Propagated Impacts")

    if not propagated_impacts:
        st.info(
            "No downstream entities were affected by this signal."
        )
        return

    propagated_impacts = sorted(
        propagated_impacts,
        key=lambda impact: abs(impact.impact_score),
        reverse=True,
    )

    for impact in propagated_impacts:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Entity",
                impact.entity_name,
            )

            col2.metric(
                "Impact",
                f"{impact.impact_score:+.3f}",
            )

            col3.metric(
                "Hop Count",
                impact.hop_count
                if impact.hop_count is not None
                else "—",
            )

            col4.metric(
                "Propagation Weight",
                (
                    f"{impact.propagation_weight:+.3f}"
                    if impact.propagation_weight is not None
                    else "—"
                ),
            )

            detail_cols = st.columns(2)

            with detail_cols[0]:
                if impact.relationship_strength is not None:
                    st.write(
                        "**Relationship Strength:** "
                        f"{impact.relationship_strength:.1%}"
                    )

            with detail_cols[1]:
                if impact.relationship_confidence is not None:
                    st.write(
                        "**Relationship Confidence:** "
                        f"{impact.relationship_confidence:.1%}"
                    )

            if impact.reason:
                st.markdown("**Propagation Path**")
                st.code(impact.reason)
