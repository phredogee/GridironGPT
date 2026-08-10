import streamlit as st


def render_signal_summary(result):
    """
    Display an analyst-friendly summary of the processed signal.
    """
    st.markdown("### Signal Summary")

    signal = result.signal

    if signal is None:
        st.info("No signal was generated.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sentiment",
            signal.sentiment.upper(),
        )

    with col2:
        st.metric(
            "Impact Score",
            f"{signal.impact_score:+.2f}",
        )

    with col3:
        st.metric(
            "Confidence",
            f"{signal.confidence * 100:.0f}%",
        )

    st.write(f"**Signal Type:** {signal.signal_type}")

    keyword_col1, keyword_col2 = st.columns(2)

    with keyword_col1:
        st.markdown("**Positive Indicators**")

        if signal.positive_hits:
            for keyword in signal.positive_hits:
                st.write(f"- {keyword}")
        else:
            st.caption("No positive indicators detected.")

    with keyword_col2:
        st.markdown("**Negative Indicators**")

        if signal.negative_hits:
            for keyword in signal.negative_hits:
                st.write(f"- {keyword}")
        else:
            st.caption("No negative indicators detected.")
