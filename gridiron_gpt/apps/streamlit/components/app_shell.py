from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

import streamlit as st


class NavigationItem(TypedDict):
    label: str
    description: str


NAVIGATION_ITEMS: Final[dict[str, NavigationItem]] = {
    "Dashboard": {
        "label": "Dashboard",
        "description": (
            "Monitor recommendations, signal activity, and the strongest "
            "fantasy-football opportunities."
        ),
    },
    "Advisor": {
        "label": "Advisor",
        "description": (
            "Ask roster, waiver, trade, and lineup questions using "
            "Gridiron Cortex intelligence."
        ),
    },
    "Players": {
        "label": "Players",
        "description": (
            "Review player scorecards, recommendations, confidence, "
            "and supporting signals."
        ),
    },
    "Trends": {
        "label": "Trends",
        "description": (
            "Track emerging player movement and changes in fantasy value."
        ),
    },
    "Trajectory": {
        "label": "Trajectory",
        "description": (
            "Inspect score history, velocity, and longer-term player direction."
        ),
    },
    "Inspector": {
        "label": "Inspector",
        "description": (
            "Inspect Cortex entities, signals, impacts, propagation, "
            "recommendations, and explanations."
        ),
    },
}


APP_NAME: Final[str] = "GRIDIRONGPT"
APP_TAGLINE: Final[str] = "Fantasy Intelligence Platform"
ENGINE_NAME: Final[str] = "Cortex Engine"
DEFAULT_MODEL: Final[str] = "Qwen3:8B"
DEFAULT_SIGNAL_COUNT: Final[int] = 601

_COMPONENT_DIR = Path(__file__).resolve().parent
_ASSET_DIR = _COMPONENT_DIR.parent / "assets"
_LOGO_PATH = _ASSET_DIR / "cortex_node.png"


def _inject_shell_styles() -> None:
    """Apply sidebar and shell-specific styling."""

    st.markdown(
        """
        <style>
        /* Sidebar layout */
        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
            height: 100vh;
            padding-bottom: 4.4rem;
        }

        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.35rem;
        }

        /* Branding */
        .gridiron-shell-brand {
            text-align: center;
            margin: 0 auto 0.8rem;
        }

        .gridiron-shell-name {
            color: var(--cortex-text);
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: 0.075em;
            line-height: 1.15;
            margin-top: 0.3rem;
        }

        .gridiron-shell-tagline {
            color: var(--cortex-muted);
            font-size: 0.77rem;
            letter-spacing: 0.035em;
            line-height: 1.35;
            margin-top: 0.3rem;
        }

        .gridiron-shell-powered {
            color: var(--cortex-muted);
            font-size: 0.68rem;
            letter-spacing: 0.08em;
            margin-top: 0.55rem;
            text-transform: uppercase;
        }

        .gridiron-shell-engine {
            color: var(--cortex-cyan);
            font-size: 0.83rem;
            font-weight: 650;
            letter-spacing: 0.025em;
            margin-top: 0.08rem;
        }

        .gridiron-shell-divider {
            border-top: 1px solid var(--cortex-border);
            margin: 0.8rem 0 0.7rem;
        }

        /* Navigation */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.26rem;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            min-height: 2.45rem;
            margin: 0;
            padding: 0.52rem 0.78rem;
            border: 1px solid transparent;
            border-radius: 7px;
            background: transparent;
            transition:
                background-color 0.16s ease,
                border-color 0.16s ease,
                color 0.16s ease;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background: rgba(47, 158, 87, 0.10);
            border-color: rgba(79, 200, 121, 0.24);
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] > label:has(input:checked) {
            background:
                linear-gradient(
                    90deg,
                    rgba(31, 95, 56, 0.95),
                    rgba(47, 158, 87, 0.58)
                );
            border-color: var(--gridiron-green-light);
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] > label p {
            color: var(--cortex-text);
            font-size: 0.92rem;
            font-weight: 550;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] > label:has(input:checked) p {
            color: #ffffff;
            font-weight: 700;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] [data-testid="stMarkdownContainer"] {
            width: 100%;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] div[data-testid="stRadio"] {
            width: 100%;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] input {
            display: none;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] div:first-child {
            margin: 0;
        }

        /* Fixed centered status line */
        .gridiron-status-bar {
            position: fixed;
            left: 0;
            bottom: 0;
            width: var(--sidebar-width, 21rem);
            box-sizing: border-box;
            z-index: 999;
            padding: 0.78rem 0.6rem 0.85rem;
            border-top: 1px solid var(--cortex-border);
            background: rgba(8, 17, 13, 0.97);
            backdrop-filter: blur(8px);
            color: var(--cortex-muted);
            text-align: center;
            font-size: 0.67rem;
            line-height: 1.35;
            white-space: nowrap;
        }

        .gridiron-status-online {
            color: var(--gridiron-green-light);
            font-weight: 700;
        }

        .gridiron-status-engine {
            color: var(--cortex-cyan);
            font-weight: 650;
        }

        /* Main page header */
        .gridiron-page-header {
            padding: 0.25rem 0 0.35rem;
        }

        .gridiron-page-kicker {
            color: var(--gridiron-green-light);
            font-size: 0.69rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .gridiron-page-title {
            color: var(--cortex-text);
            font-size: 1.72rem;
            font-weight: 760;
            letter-spacing: -0.025em;
            line-height: 1.2;
            margin-top: 0.2rem;
        }

        .gridiron-page-description {
            color: var(--cortex-muted);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-top: 0.28rem;
            max-width: 58rem;
        }

        @media (max-width: 900px) {
            .gridiron-status-bar {
                position: static;
                width: 100%;
                margin-top: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand() -> None:
    """Render the GridironGPT product identity."""

    if _LOGO_PATH.exists():
        st.image(str(_LOGO_PATH), use_container_width=True)

    st.markdown(
        f"""
        <div class="gridiron-shell-brand">
            <div class="gridiron-shell-name">{APP_NAME}</div>
            <div class="gridiron-shell-tagline">{APP_TAGLINE}</div>
            <div class="gridiron-shell-powered">Powered by</div>
            <div class="gridiron-shell-engine">{ENGINE_NAME}</div>
        </div>
        <div class="gridiron-shell-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def _render_navigation() -> str:
    """Render icon-free navigation and return the selected page key."""

    page_keys = list(NAVIGATION_ITEMS.keys())

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = page_keys[0]

    current_page = st.session_state.selected_page
    default_index = (
        page_keys.index(current_page)
        if current_page in page_keys
        else 0
    )

    selected_page = st.radio(
        "Navigation",
        options=page_keys,
        index=default_index,
        format_func=lambda key: NAVIGATION_ITEMS[key]["label"],
        label_visibility="collapsed",
        key="sidebar_navigation",
    )

    st.session_state.selected_page = selected_page
    return selected_page


def _render_status_bar(
    *,
    version: str,
    model_name: str,
    signal_count: int | str,
) -> None:
    """Render a compact centered engine status bar."""

    display_version = version if str(version).startswith("v") else f"v{version}"

    st.markdown(
        f"""
        <div class="gridiron-status-bar">
            <span class="gridiron-status-online">Online</span>
            &nbsp;|&nbsp;
            <span class="gridiron-status-engine">{ENGINE_NAME}</span>
            &nbsp;|&nbsp;
            {model_name}
            &nbsp;|&nbsp;
            {signal_count} Signals
            &nbsp;|&nbsp;
            {display_version}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    *,
    version: str,
    model_name: str = DEFAULT_MODEL,
    signal_count: int | str = DEFAULT_SIGNAL_COUNT,
) -> str:
    """
    Render the application sidebar and return the selected page.

    Existing callers only need to pass ``version``. Model and signal values
    remain optional so they can be connected to live application data later.
    """

    _inject_shell_styles()

    with st.sidebar:
        _render_brand()
        selected_page = _render_navigation()
        _render_status_bar(
            version=version,
            model_name=model_name,
            signal_count=signal_count,
        )

    return selected_page


def render_shell_header(
    *,
    page_name: str,
    description: str,
) -> None:
    """Render a consistent header for the active application page."""

    st.markdown(
        f"""
        <div class="gridiron-page-header">
            <div class="gridiron-page-kicker">{APP_NAME}</div>
            <div class="gridiron-page-title">{page_name}</div>
            <div class="gridiron-page-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
