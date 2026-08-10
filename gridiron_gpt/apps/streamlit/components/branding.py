from pathlib import Path

import streamlit as st


ASSET_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "assets"
)

CORTEX_LOGO = (
    ASSET_DIRECTORY
    / "cortex_engine_wallpaper.png"
)


def get_project_version() -> str:
    version_file = Path("VERSION")

    if version_file.exists():
        return version_file.read_text(
            encoding="utf-8"
        ).strip()

    return "unknown"


def render_branding(
    application_name: str = "GridironGPT",
) -> None:
    """Render the shared Cortex-powered application header."""

    version = get_project_version()

    left_spacer, center_col, status_col = st.columns(
        [1.2, 5, 1.2],
        vertical_alignment="center",
    )

    with left_spacer:
        st.empty()

    with center_col:
        st.html(
            f"""
            <div class="cortex-brand-header">
                <div class="cortex-app-name">{application_name}</div>
                <div class="cortex-powered-label">Powered by</div>
                <div class="cortex-engine-name">Cortex Engine</div>
                <div class="cortex-brand-line"></div>
            </div>
             """
        )


    with status_col:
        logo_col, status_text_col = st.columns(
            [1, 1.8],
            vertical_alignment="center",
        )

        with logo_col:
            if CORTEX_LOGO.exists():
                st.image(
                    str(CORTEX_LOGO),
                    width=78,
                )

        with status_text_col:
            st.html(
                f"""
                <div class="cortex-status-wrapper">
                    <div class="cortex-status-pill">
                        <span class="cortex-status-dot"></span>
                        Online
                    </div>
                    <div class="cortex-version">v{version}</div>
                </div>
                """
            )
