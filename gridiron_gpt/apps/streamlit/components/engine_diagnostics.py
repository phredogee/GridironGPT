import streamlit as st


def render_engine_diagnostics(result):
    st.markdown("### 🔧 Engine Diagnostics")
    st.caption("Internal Cortex objects and pipeline output.")

    with st.expander("📥 Raw Event"):
        st.json(result.event.__dict__)

    with st.expander("👥 Resolved Entities"):
        st.json([entity.__dict__ for entity in result.entities])

    with st.expander("📡 Signal"):
        if result.signal:
            st.json(
                {
                    **result.signal.__dict__,
                    "entities": [
                        entity.__dict__
                        for entity in result.signal.entities
                    ],
                }
            )

    with st.expander("🔗 Impacts"):
        st.json([impact.__dict__ for impact in result.impacts])

    with st.expander("📈 Score Updates"):
        st.json([update.__dict__ for update in result.score_updates])

    with st.expander("🎯 Recommendations"):
        st.json([rec.__dict__ for rec in result.recommendations])

    with st.expander("🧠 Engine Result"):
        st.write(result)
