import streamlit as st


FACULTY_ORDER = {
    "Observe": 1,
    "Understand": 2,
    "Reason": 3,
    "Evaluate": 4,
    "Predict": 5,
    "Decide": 6,
    "Explain": 7,
    "Remember": 8,
}


def render_cognitive_trace(result):
    """Render structured EvidenceChain objects as a cognitive trace."""

    st.markdown("### Cognitive Trace")

    if not result.evidence_chains:
        st.info("No structured evidence chain was generated.")
        return

    for chain_index, chain in enumerate(
        result.evidence_chains,
        start=1,
    ):
        if len(result.evidence_chains) > 1:
            st.markdown(
                f"#### Chain {chain_index}: {chain.entity_name}"
            )

        summary_col1, summary_col2, summary_col3 = st.columns(3)

        with summary_col1:
            st.metric("Entity", chain.entity_name)

        with summary_col2:
            st.metric("Decision", chain.action)

        with summary_col3:
            st.metric(
                "Confidence",
                f"{chain.confidence:.1f}%",
            )

        ordered_steps = sorted(
            chain.steps,
            key=lambda step: FACULTY_ORDER.get(
                step.faculty,
                99,
            ),
        )

        for index, step in enumerate(ordered_steps):
            with st.container(border=True):
                header_col, value_col = st.columns([3, 1])

                with header_col:
                    st.markdown(
                        f"#### {step.faculty}"
                    )
                    st.write(step.summary)

                with value_col:
                    if step.value is not None:
                        st.metric(
                            step.step_type.replace(
                                "_",
                                " ",
                            ).title(),
                            _format_value(step.value),
                        )

                if step.entity_name:
                    st.caption(
                        f"Entity: {step.entity_name}"
                    )

                if step.reasons:
                    with st.expander("Evidence"):
                        for reason in step.reasons:
                            st.write(f"- {reason}")

            if index < len(ordered_steps) - 1:
                st.markdown(
                    "<div style='text-align:center;"
                    "font-size:1.5rem;'>↓</div>",
                    unsafe_allow_html=True,
                )


def _format_value(value):
    if isinstance(value, float):
        if 0.0 <= value <= 1.0:
            return f"{value * 100:.0f}%"

        return f"{value:+.2f}"

    return str(value)
