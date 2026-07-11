from pathlib import Path
import streamlit as st


def get_project_version():
    version_file = Path("VERSION")

    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()

    return "unknown"


def render_branding():
    version = get_project_version()

    st.markdown(
        f"""
# 🧠 GRIDIRON CORTEX

## The Intelligence Engine

### Running inside GridironGPT

`Engine v{version} — Typed pipeline enabled`
        """
    )
