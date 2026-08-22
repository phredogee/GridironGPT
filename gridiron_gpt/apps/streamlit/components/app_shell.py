from __future__ import annotations

import base64
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
    "Dashboard": {"label": "Dashboard", "description": "Monitor recommendations, signal activity, and the strongest fantasy-football opportunities."},
    "Explorer": {"label": "Cortex Explorer", "description": "Open a unified player dossier with score, confidence, evidence, trend, trajectory, and Cortex profile."},
    "Advisor": {"label": "Advisor", "description": "Ask roster, waiver, trade, and lineup questions using Gridiron Cortex intelligence."},
    "Rankings": {"label": "Rankings", "description": "Review integrated fantasy rankings with historical, market, role, Cortex, availability, and evidence-based explanations."},
    "Players": {"label": "Players", "description": "Review player scorecards, recommendations, confidence, and supporting signals."},
    "Trends": {"label": "Trends", "description": "Track emerging player movement and changes in fantasy value."},
    "Trajectory": {"label": "Trajectory", "description": "Inspect score history, velocity, and longer-term player direction."},
    "Ingestion": {"label": "Ingestion", "description": "Monitor provider health, ingestion reliability, run metrics, and recent operational history."},
    "Inspector": {"label": "Inspector", "description": "Inspect Cortex entities, signals, impacts, propagation, recommendations, and explanations."},
}

NAVIGATION_SECTIONS: Final[tuple[NavigationSection, ...]] = (
    {"label": "Intelligence", "icon": "🧠", "pages": ("Dashboard", "Explorer", "Players", "Trends", "Trajectory", "Inspector")},
    {"label": "Fantasy", "icon": "🏈", "pages": ("Rankings", "Advisor")},
    {"label": "Operations", "icon": "⚙", "pages": ("Ingestion",)},
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
    st.markdown("""
<style>
section[data-testid="stSidebar"] {background:#050706!important;border-right:1px solid rgba(82,214,124,.22)}
section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {height:100vh;padding-bottom:4.4rem;background:#050706!important}
.gridiron-home-link{display:block;max-width:14rem;margin:0 auto .4rem;padding:.3rem;border-radius:50%;background:#050706;text-decoration:none!important;transition:transform 170ms ease,filter 170ms ease,box-shadow 170ms ease}.gridiron-home-link:hover{transform:scale(1.025);filter:brightness(1.12);box-shadow:0 0 22px rgba(86,239,132,.26)}.gridiron-home-logo{display:block;width:100%;border-radius:50%;background:#050706}.gridiron-shell-brand{text-align:center;margin:0 auto .8rem}.gridiron-shell-name{color:var(--cortex-text);font-size:1.55rem;font-weight:800;letter-spacing:.075em;line-height:1.15;margin-top:.3rem}.gridiron-shell-tagline{color:var(--cortex-muted);font-size:.77rem;letter-spacing:.035em;line-height:1.35;margin-top:.3rem}.gridiron-shell-powered{color:var(--cortex-muted);font-size:.68rem;letter-spacing:.08em;margin-top:.55rem;text-transform:uppercase}.gridiron-shell-engine{color:var(--cortex-cyan);font-size:.83rem;font-weight:650;letter-spacing:.025em;margin-top:.08rem}.gridiron-shell-divider{border-top:1px solid rgba(82,214,124,.2);margin:.8rem 0 .7rem}
.gridiron-nav{display:flex;flex-direction:column;gap:.3rem}.gridiron-nav-section{position:relative;border:1px solid transparent;border-radius:9px;overflow:hidden;transition:border-color 170ms ease,box-shadow 170ms ease}.gridiron-nav-heading{position:relative;display:flex;align-items:center;gap:.58rem;min-height:2.55rem;padding:.56rem .78rem .56rem .88rem;color:var(--cortex-text)!important;background:rgba(14,29,20,.78);font-size:.93rem;font-weight:650;text-decoration:none!important;cursor:pointer;transition:background 170ms ease,color 170ms ease,box-shadow 170ms ease}.gridiron-nav-heading::before{content:"";position:absolute;left:0;top:.42rem;bottom:.42rem;width:3px;border-radius:2px;background:transparent}.gridiron-nav-chevron{margin-left:auto;color:var(--cortex-muted);font-size:.72rem;transition:transform 170ms ease,color 170ms ease}.gridiron-nav-section:hover,.gridiron-nav-section:focus-within{border-color:rgba(97,255,145,.48);box-shadow:0 0 14px rgba(57,222,111,.16)}.gridiron-nav-section:hover .gridiron-nav-heading,.gridiron-nav-section:focus-within .gridiron-nav-heading{color:#fff!important;background:linear-gradient(90deg,rgba(38,132,73,.96),rgba(55,201,105,.72))}.gridiron-nav-section:hover .gridiron-nav-heading::before,.gridiron-nav-section:focus-within .gridiron-nav-heading::before{background:#79ff9f;box-shadow:0 0 10px rgba(121,255,159,.85)}.gridiron-nav-section:hover .gridiron-nav-chevron,.gridiron-nav-section:focus-within .gridiron-nav-chevron,.gridiron-nav-section.active .gridiron-nav-chevron{color:#fff;transform:rotate(90deg)}.gridiron-nav-section.active .gridiron-nav-heading{background:linear-gradient(90deg,rgba(24,92,52,.98),rgba(39,132,73,.64));font-weight:760}.gridiron-nav-section.active .gridiron-nav-heading::before{background:var(--gridiron-green-light);box-shadow:0 0 8px rgba(121,255,159,.55)}
.gridiron-nav-children{display:none;padding:.34rem;background:#070b08}.gridiron-nav-section:hover>.gridiron-nav-children,.gridiron-nav-section:focus-within>.gridiron-nav-children,.gridiron-nav-section.active>.gridiron-nav-children{display:block}.gridiron-nav-child{position:relative;display:block;margin:.12rem 0;padding:.48rem .66rem .48rem 1.45rem;border-radius:7px;color:var(--cortex-muted)!important;font-size:.84rem;text-decoration:none!important;transition:background 150ms ease,color 150ms ease,transform 150ms ease}.gridiron-nav-child::before{content:"";position:absolute;left:.66rem;top:50%;width:5px;height:5px;border-radius:50%;background:rgba(112,188,133,.52);transform:translateY(-50%)}.gridiron-nav-child:hover{color:#fff!important;background:rgba(65,210,112,.19);transform:translateX(2px)}.gridiron-nav-child.active{color:#fff!important;background:rgba(47,158,87,.30);font-weight:700}.gridiron-nav-child.active::before{background:#79ff9f;box-shadow:0 0 8px rgba(121,255,159,.85)}
div[data-baseweb="select"],div[data-testid="stTextInput"],div[data-testid="stNumberInput"],div[data-testid="stDateInput"]{max-width:28rem}div[data-baseweb="select"]>div,div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input,div[data-testid="stDateInput"] input,div[data-testid="stTextArea"] textarea{background:#d7dbd8!important;color:#101713!important;border-color:#929b95!important}div[data-testid="stTextArea"] textarea::placeholder{color:#353b37!important;opacity:1!important}div[data-testid="stTextArea"] textarea{caret-color:#148443!important}div[data-baseweb="select"]>div:focus-within,div[data-testid="stTextInput"] input:focus,div[data-testid="stNumberInput"] input:focus,div[data-testid="stDateInput"] input:focus,div[data-testid="stTextArea"] textarea:focus{border-color:#55d982!important;box-shadow:0 0 0 1px #55d982!important}
.gridiron-status-bar{position:fixed;left:0;bottom:0;width:var(--sidebar-width,21rem);box-sizing:border-box;z-index:999;padding:.78rem .6rem .85rem;border-top:1px solid rgba(82,214,124,.22);background:#050706;color:var(--cortex-muted);text-align:center;font-size:.67rem;line-height:1.35;white-space:nowrap}.gridiron-status-online{color:var(--gridiron-green-light);font-weight:700}.gridiron-status-engine{color:var(--cortex-cyan);font-weight:650}.gridiron-page-header{padding:.25rem 0 .35rem}.gridiron-page-kicker{color:var(--gridiron-green-light);font-size:.69rem;font-weight:750;letter-spacing:.13em;text-transform:uppercase}.gridiron-page-title{color:var(--cortex-text);font-size:1.72rem;font-weight:760;letter-spacing:-.025em;line-height:1.2;margin-top:.2rem}.gridiron-page-description{color:var(--cortex-muted);font-size:.9rem;line-height:1.5;margin-top:.28rem;max-width:58rem}@media(max-width:900px){.gridiron-status-bar{position:static;width:100%;margin-top:1rem}}
</style>""", unsafe_allow_html=True)


def _logo_data_uri() -> str | None:
    if not _LOGO_PATH.exists(): return None
    encoded = base64.b64encode(_LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _render_brand() -> None:
    logo_uri = _logo_data_uri(); logo_markup = ""
    if logo_uri:
        logo_markup = '<a class="gridiron-home-link" href="?page=Dashboard" target="_top" title="Return to Dashboard" aria-label="Return to Dashboard">' + f'<img class="gridiron-home-logo" src="{logo_uri}" alt="Gridiron Cortex node"></a>'
    st.markdown(f'{logo_markup}<div class="gridiron-shell-brand"><div class="gridiron-shell-name">{APP_NAME}</div><div class="gridiron-shell-tagline">{APP_TAGLINE}</div><div class="gridiron-shell-powered">Powered by</div><div class="gridiron-shell-engine">{ENGINE_NAME}</div></div><div class="gridiron-shell-divider"></div>', unsafe_allow_html=True)


def build_navigation_markup(selected_page: str) -> str:
    sections = ['<nav class="gridiron-nav" aria-label="Primary navigation">']
    for section in NAVIGATION_SECTIONS:
        active_section = selected_page in section["pages"]; children = []
        for page in section["pages"]:
            item = NAVIGATION_ITEMS[page]; active = " active" if page == selected_page else ""; current = ' aria-current="page"' if page == selected_page else ""
            children.append(f'<a class="gridiron-nav-child{active}" href="?page={quote(page)}" target="_top"{current}>{escape(item["label"])}</a>')
        section_class = "gridiron-nav-section active" if active_section else "gridiron-nav-section"
        sections.append(f'<div class="{section_class}" tabindex="0"><div class="gridiron-nav-heading"><span>{escape(section["icon"])}</span><span>{escape(section["label"])}</span><span class="gridiron-nav-chevron">›</span></div><div class="gridiron-nav-children">{"".join(children)}</div></div>')
    sections.append("</nav>"); return "".join(sections)


def _resolve_selected_page() -> str:
    requested = st.query_params.get("page", "Dashboard")
    if isinstance(requested, list): requested = requested[0] if requested else "Dashboard"
    return requested if requested in NAVIGATION_ITEMS else "Dashboard"


def render_sidebar(*, version: str, model_name: str = DEFAULT_MODEL, signal_count: int = DEFAULT_SIGNAL_COUNT) -> str:
    _inject_shell_styles(); selected_page = _resolve_selected_page()
    with st.sidebar:
        _render_brand(); st.markdown(build_navigation_markup(selected_page), unsafe_allow_html=True)
        st.markdown(f'<div class="gridiron-status-bar"><span class="gridiron-status-online">● System Online</span>&nbsp;&nbsp;|&nbsp;&nbsp;<span class="gridiron-status-engine">{escape(ENGINE_NAME)}</span>&nbsp;&nbsp;|&nbsp;&nbsp;Model: {escape(model_name)}&nbsp;&nbsp;|&nbsp;&nbsp;Signals: {signal_count:,}&nbsp;&nbsp;|&nbsp;&nbsp;v{escape(version)}</div>', unsafe_allow_html=True)
    return selected_page


def render_shell_header(*, page_name: str, description: str) -> None:
    st.markdown(f'<div class="gridiron-page-header"><div class="gridiron-page-kicker">GridironGPT / Cortex</div><div class="gridiron-page-title">{escape(page_name)}</div><div class="gridiron-page-description">{escape(description)}</div></div>', unsafe_allow_html=True)
