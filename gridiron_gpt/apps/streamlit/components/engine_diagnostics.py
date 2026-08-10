from dataclasses import asdict, is_dataclass

import streamlit as st


def render_engine_diagnostics(result):
    st.markdown("### Engine Diagnostics")
    st.caption("Internal Cortex objects and pipeline output.")

    with st.expander("Raw Event"):
        st.json(_serialize(result.event))

    with st.expander("Resolved Entities"):
        st.json(_serialize(result.entities))

    with st.expander("Signal"):
        if result.signal:
            st.json(_serialize(result.signal))
        else:
            st.info("No signal generated.")

    with st.expander("Impacts"):
        st.json(_serialize(result.impacts))

    with st.expander("Score Updates"):
        st.json(_serialize(result.score_updates))

    with st.expander("Player Scorecards"):
        st.json(_serialize(result.player_scorecards))

    with st.expander("Scorecard History"):
        st.json(_serialize(result.scorecard_history))

    with st.expander("Predictions"):
        st.json(_serialize(result.predictions))

    with st.expander("Recommendations"):
        st.json(_serialize(result.recommendations))

    with st.expander("Evidence Chains"):
        st.json(_serialize(result.evidence_chains))

    with st.expander("Evidence Graphs"):
        st.json(_serialize(result.evidence_graphs))

    with st.expander("Complete Engine Result"):
        st.json(_serialize(result))


def _serialize(value):
    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, list):
        return [
            _serialize(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    return value
