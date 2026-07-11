import streamlit as st


def render_recommendation_card(result):
    st.markdown("### Recommendation Summary")

    if not result.recommendations:
        st.info("No recommendation generated.")
        return

    for rec in result.recommendations:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Action", rec.action)

        with col2:
            st.metric("Confidence", f"{rec.confidence}%")

        with col3:
            st.metric("Score Delta", f"{rec.score_delta:+.2f}")

        st.write(f"**Player:** {rec.entity_name} ({rec.team or 'UNK'})")

        if rec.reasons:
            st.markdown("**Reasons**")
            for reason in rec.reasons:
                st.write(f"- {reason}")
