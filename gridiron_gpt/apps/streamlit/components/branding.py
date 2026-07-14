from pathlib import Path

import streamlit as st


def get_project_version():
    version_file = Path("VERSION")

    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()

    return "unknown"


def render_branding():
    version = get_project_version()

    st.title("🧠 GRIDIRON CORTEX")

    st.subheader(
        "The football intelligence implementation of Cortex Engine"
    )

    st.caption(
        f"Running inside GridironGPT · "
        f"Engine v{version} · Typed pipeline enabled"
    )

    st.info(
        "Gridiron Cortex transforms NFL news, structured statistics, "
        "historical trends, and player relationships into scored, "
        "explainable fantasy-football recommendations."
    )

    st.markdown("### Platform Architecture")

    application_col, domain_col, engine_col = st.columns(3)

    with application_col:
        st.markdown("#### GridironGPT")
        st.caption("Application")
        st.write(
            "The user-facing fantasy football experience for dashboards, "
            "player intelligence, roster advice, and recommendations."
        )

    with domain_col:
        st.markdown("#### Gridiron Cortex")
        st.caption("Domain intelligence")
        st.write(
            "The football-specific layer that understands NFL players, "
            "teams, usage, news, statistics, and relationships."
        )

    with engine_col:
        st.markdown("#### Cortex Engine")
        st.caption("Core platform")
        st.write(
            "The reusable evidence and decision intelligence architecture "
            "behind signal generation, aggregation, propagation, scoring, "
            "recommendations, and explanations."
        )

    with st.expander("About Cortex Engine"):
        st.markdown(
            """
            Cortex Engine is the broader intelligence architecture behind
            this project.

            It is designed to:

            - ingest evidence from multiple sources;
            - normalize events and entities;
            - generate structured signals;
            - aggregate supporting or conflicting evidence;
            - propagate effects through relationships;
            - update scores and recommendations;
            - explain how each conclusion was reached.

            Gridiron Cortex is the first domain implementation of Cortex
            Engine, and GridironGPT is the application built on top of it.
            """
        )
