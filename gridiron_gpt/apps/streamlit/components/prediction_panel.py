import streamlit as st


def render_prediction_panel(result):
    """Render forecasts produced by the Cortex Predict faculty."""

    st.markdown("### Prediction")

    if not result.predictions:
        st.info("No prediction was generated.")
        return

    for prediction in result.predictions:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Trend",
                prediction.projected_trend,
            )

        with col2:
            st.metric(
                "Projected Score",
                f"{prediction.projected_score:.2f}",
                delta=f"{prediction.score_delta:+.2f}",
            )

        with col3:
            st.metric(
                "Confidence",
                f"{prediction.confidence * 100:.0f}%",
            )

        with col4:
            st.metric(
                "Horizon",
                f"{prediction.horizon_days} days",
            )

        st.write(
            f"**Entity:** {prediction.entity_name}"
        )

        if prediction.reasons:
            st.markdown("**Forecast reasons**")

            for reason in prediction.reasons:
                st.write(f"- {reason}")
