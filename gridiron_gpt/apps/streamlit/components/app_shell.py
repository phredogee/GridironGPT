from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Final, TypedDict
from urllib.parse import quote

import streamlit as st


class NavigationItem(TypedDict):
    label: str
    description: str


class NavigationSection(TypedDict):
    label: str
    icon: str
    pages: tuple[str, ...]


NAVIGATION_ITEMS: Final[dict[str, NavigationItem]] = {
    "Dashboard": {
        "label": "Dashboard",
        "description": "Monitor recommendations, signal activity, and the strongest fantasy-football opportunities.",
    },
    "Advisor": {
        "label": "Advisor",
        "description": "Ask roster, waiver, trade, and lineup questions using Gridiron Cortex intelligence.",
    },
    "Players": {
        "label": "Players",
        "description": "Review player scorecards, recommendations, confidence, and supporting signals.",
    },
    "Trends": {
        "label": "Trends",
        "description": "Track emerging player movement and changes in fantasy value.",
    },
    "Trajectory": {
        "label": "Trajectory",
        "description": "Inspect score history, velocity, and longer-term player direction.",
    },
    "Ingestion": {
        "label": "Ingestion",
        "description": "Monitor provider health, ingestion reliability, run metrics, and recent operational history.",
    },
    "Inspector": {
        "label": "Inspector",
        "description": "Inspect Cortex entities, signals, impacts, propagation, recommendations, and explanations.",
    },
}

NAVIGATION_SECTIONS: Final[tuple[NavigationSection, ...]] = (
    {
        "label": "Intelligence",
        "icon": "🧠",
        "pages": ("Dashboard", "Players", "Trends", "Trajectory", "Inspector"),
    },
    {
        "label": "Fantasy",
        "icon": "🏈",
        "pages": ("Advisor",),
    },
    {
        "label": "Operations",
        "icon": "⚙",
        "pages": ("Ingestion",),
    },
)

APP_NAME: Final[str] = "GRIDIRONGPT"
APP_TAGLINE: Final[str] = "Fantasy Intelligence Platform"
ENGINE_NAME: Final[str] = "Cortex Engine"
DEFAULT_MODEL: Final[str] = "Qwen3:8B"
DEFAULT_SIGNAL_COUNT: Final[int] = 601

_COMPONENT_DIR = Path(__file__).resolve().parent
_ASSET_DIR = _COMPONENT_DIR.parent / "assets"
_LOGO_PATH = _ASSET_DIR / "cortex_node.png"


def _inject_shell_styles() -> None:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
            height: 100vh;
            padding-bottom: 4.4rem;
        }

        .gridiron-shell-brand { text-align: center; margin: 0 auto 0.8rem; }
        .gridiron-shell-name {
            color: var(--cortex-text); font-size: 1.55rem; font-weight: 800;
            letter-spacing: 0.075em; line-height: 1.15; margin-top: 0.3rem;
        }
        .gridiron-shell-tagline {
            color: var(--cortex-muted); font-size: 0.77rem;
            letter-spacing: 0.035em; line-height: 1.35; margin-top: 0.3rem;
        }
        .gridiron-shell-powered {
            color: var(--cortex-muted); font-size: 0.68rem;
            letter-spacing: 0.08em; margin-top: 0.55rem; text-transform: uppercase;
        }
        .gridiron-shell-engine {
            color: var(--cortex-cyan); font-size: 0.83rem; font-weight: 650;
            letter-spacing: 0.025em; margin-top: 0.08rem;
        }
        .gridiron-shell-divider {
            border-top: 1px solid var(--cortex-border); margin: 0.8rem 0 0.7rem;
        }

        .gridiron-nav { display: flex; flex-direction: column; gap: 0.3rem; }
        .gridiron-nav-section {
            border: 1px solid transparent;
            border-radius: 9px;
            overflow: hidden;
            transition: border-color 170ms ease, box-shadow 170ms ease;
        }
        .gridiron-nav-heading {
            position: relative;
            display: flex;
            align-items: center;
            gap: 0.58rem;
            min-height: 2.55rem;
            padding: 0.56rem 0.78rem 0.56rem 0.88rem;
            color: var(--cortex-text) !important;
            background: rgba(19, 43, 30, 0.42);
            font-size: 0.93rem;
            font-weight: 650;
            text-decoration: none !important;
            transition: background 170ms ease, color 170ms ease, box-shadow 170ms ease;
        }
        .gridiron-nav-heading::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0.42rem;
            bottom: 0.42rem;
            width: 3px;
            border-radius: 2px;
            background: transparent;
            transition: background 170ms ease, box-shadow 170ms ease;
        }
        .gridiron-nav-chevron {
            margin-left: auto;
            color: var(--cortex-muted);
            font-size: 0.72rem;
            transform: rotate(0deg);
            transition: transform 170ms ease, color 170ms ease;
        }
        .gridiron-nav-section:hover {
            border-color: rgba(97, 255, 145, 0.48);
            box-shadow: 0 0 14px rgba(57, 222, 111, 0.16);
        }
        .gridiron-nav-section:hover .gridiron-nav-heading {
            color: #ffffff !important;
            background: linear-gradient(90deg, rgba(38, 132, 73, 0.94), rgba(55, 201, 105, 0.68));
            box-shadow: inset 0 0 18px rgba(113, 255, 157, 0.13);
        }
        .gridiron-nav-section:hover .gridiron-nav-heading::before {
            background: #79ff9f;
            box-shadow: 0 0 10px rgba(121, 255, 159, 0.85);
        }
        .gridiron-nav-section:hover .gridiron-nav-chevron {
            color: #ffffff;
            transform: rotate(90deg);
        }
        .gridiron-nav-section.active .gridiron-nav-heading {
            background: linear-gradient(90deg, rgba(24, 92, 52, 0.96), rgba(39, 132, 73, 0.60));
            font-weight: 760;
        }
        .gridiron-nav-section.active .gridiron-nav-heading::before {
            background: var(--gridiron-green-light);
        }

        .gridiron-nav-children {
            max-height: 0;
            opacity: 0;
            overflow: hidden;
            padding: 0 0.34rem;
            background: rgba(7, 18, 12, 0.58);
            transition: max-height 210ms ease, opacity 150ms ease, padding 210ms ease;
        }
        .gridiron-nav-section:hover .gridiron-nav-children {
            max-height: 22rem;
            opacity: 1;
            padding: 0.34rem;
        }
        .gridiron-nav-child {
            position: relative;
            display: block;
            margin: 0.12rem 0;
            padding: 0.48rem 0.66rem 0.48rem 1.45rem;
            border-radius: 7px;
            color: var(--cortex-muted) !important;
            font-size: 0.84rem;
            text-decoration: none !important;
            transition: background 150ms ease, color 150ms ease, transform 150ms ease;
        }
        .gridiron-nav-child::before {
            content: "";
            position: absolute;
            left: 0.66rem;
            top: 50%;
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: rgba(112, 188, 133, 0.52);
            transform: translateY(-50%);
        }
        .gridiron-nav-child:hover {
            color: #ffffff !important;
            background: rgba(65, 210, 112, 0.19);
            transform: translateX(2px);
        }
        .gridiron-nav-child.active {
            color: #ffffff !important;
            background: rgba(47, 158, 87, 0.30);
            font-weight: 700;
        }
        .gridiron-nav-child.active::before {
            background: #79ff9f;
            box-shadow: 0 0 8px rgba(121, 255, 159, 0.85);
        }

        /* Compact, high-contrast controls throughout the application. */
        div[data-baseweb="select"],
        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stDateInput"] {
            max-width: 28rem;
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #d7dbd8 !important;
            color: #101713 !important;
            border-color: #929b95 !important;
        }
        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stDateInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #55d982 !important;
            box-shadow: 0 0 0 1px #55d982 !important;
        }

        .gridiron-status-bar {
            position: fixed; left: 0; bottom: 0; width: var(--sidebar-width, 21rem);
            box-sizing: border-box; z-index: 999; padding: 0.78rem 0.6rem 0.85rem;
            border-top: 1px solid var(--cortex-border); background: rgba(8, 17, 13, 0.97);
            backdrop-filter: blur(8px); color: var(--cortex-muted); text-align: center;
            font-size: 0.67rem; line-height: 1.35; white-space: nowrap;
        }
        .gridiron-status-online { color: var(--gridiron-green-light); font-weight: 700; }
        .gridiron-status-engine { color: var(--cortex-cyan); font-weight: 650; }
        .gridiron-page-header { padding: 0.25rem 0 0.35rem; }
        .gridiron-page-kicker {
            color: var(--gridiron-green-light); font-size: 0.69rem;
            font-weight: 750; letter-spacing: 0.13em; text-transform: uppercase;
        }
        .gridiron-page-title {
            color: var(--cortex-text); font-size: 1.72rem; font-weight: 760;
            letter-spacing: -0.025em; line-height: 1.2; margin-top: 0.2rem;
        }
        .gridiron-page-description {
            color: var(--cortex-muted); font-size: 0.9rem; line-height: 1.5;
            margin-top: 0.28rem; max-width: 58rem;
        }
        @media (max-width: 900px) {
            .gridiron-status-bar { position: static; width: 100%; margin-top: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand() -> None:
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


def build_navigation_markup(selected_page: str) -> str:
    sections: list[str] = ['<nav class="gridiron-nav" aria-label="Primary navigation">']
    for section in NAVIGATION_SECTIONS:
        active_section = selected_page in section["pages"]
        children = []
        for page in section["pages"]:
            item = NAVIGATION_ITEMS[page]
            active = " active" if page == selected_page else ""
            children.append(
                f'<a class="gridiron-nav-child{active}" href="?page={quote(page)}" '
                f'aria-current="page"' if page == selected_page else
                f'<a class="gridiron-nav-child{active}" href="?page={quote(page)}"'
            )
            children[-1] += f'>{escape(item["label"])}</a>'

        section_class = "gridiron-nav-section active" if active_section else "gridiron-nav-section"
        sections.append(
            f'<div class="{section_class}">'
            f'<div class="gridiron-nav-heading">'
            f'<span>{escape(section["icon"])}</span>'
            f'<span>{escape(section["label"])}</span>'
            f'<span class="gridiron-nav-chevron">›</span>'
            f'</div>'
            f'<div class="gridiron-nav-children">{"".join(children)}</div>'
            f'</div>'
        )
    sections.append("</nav>")
    return "".join(sections)


def _render_navigation() -> str:
    requested = st.query_params.get("page", "Dashboard")
    selected_page = requested if requested in NAVIGATION_ITEMS else "Dashboard"
    st.session_state.selected_page = selected_page
    st.markdown(build_navigation_markup(selected_page), unsafe_allow_html=True)
    return selected_page


def _render_status_bar(*, version: str, model_name: str, signal_count: int | str) -> None:
    display_version = version if str(version).startswith("v") else f"v{version}"
    st.markdown(
        f"""
        <div class="gridiron-status-bar">
            <span class="gridiron-status-online">Online</span>&nbsp;|&nbsp;
            <span class="gridiron-status-engine">{ENGINE_NAME}</span>&nbsp;|&nbsp;
            {model_name}&nbsp;|&nbsp;{signal_count} Signals&nbsp;|&nbsp;{display_version}
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
    _inject_shell_styles()
    with st.sidebar:
        _render_brand()
        selected_page = _render_navigation()
        _render_status_bar(version=version, model_name=model_name, signal_count=signal_count)
    return selected_page


def render_shell_header(*, page_name: str, description: str) -> None:
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
