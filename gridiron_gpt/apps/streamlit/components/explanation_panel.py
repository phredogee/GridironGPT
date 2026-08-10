import streamlit as st


def render_explanation_panel(result):
    st.markdown("### Explanation")
    st.write(result.explanation)
