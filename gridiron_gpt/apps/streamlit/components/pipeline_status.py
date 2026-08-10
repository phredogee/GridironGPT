import streamlit as st


def render_pipeline_status(result):
    st.markdown("### Pipeline Status")
    st.caption(
        "Execution status for the major Gridiron Cortex reasoning stages."
    )

    stages = [
        (
            "Evidence",
            result.canonical_event is not None,
        ),
        (
            "Confidence",
            result.confidence_result is not None,
        ),
        (
            "Entities",
            bool(result.entities),
        ),
        (
            "Signal",
            result.signal is not None,
        ),
        (
            "Propagation",
            bool(result.impacts),
        ),
        (
            "Scores",
            bool(result.score_updates),
        ),
        (
            "Prediction",
            bool(result.predictions),
        ),
        (
            "Recommendation",
            bool(result.recommendations),
        ),
        (
            "Explanation",
            bool(result.explanation),
        ),
    ]

    status_cols = st.columns(3)

    for index, (label, passed) in enumerate(stages):
        with status_cols[index % 3]:
            if passed:
                st.success(f"✓ {label}")
            else:
                st.warning(f"⚠ {label}")
