import streamlit as st


def render_pipeline_status(result):
    st.markdown("### Pipeline Status")

    status_cols = st.columns(6)

    stages = [
        ("RawEvent", True),
        ("Entities", bool(result.entities)),
        ("Signal", result.signal is not None),
        ("Impacts", bool(result.impacts)),
        ("Scores", bool(result.score_updates)),
        ("Recommendation", bool(result.recommendations)),
    ]

    for col, (label, passed) in zip(status_cols, stages):
        with col:
            st.metric(label, "✅" if passed else "⚠️")
