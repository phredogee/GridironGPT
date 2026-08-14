import streamlit as st


def apply_cortex_theme() -> None:
    """Apply the GridironGPT visual theme powered by Cortex Engine."""

    st.markdown(
        """
        <style>
        :root {
            --cortex-bg: #08110d;
            --cortex-surface: #101a15;
            --cortex-surface-2: #15231b;
            --cortex-border: #294235;
            --cortex-text: #f3f7f4;
            --cortex-muted: #9caf9f;
            --cortex-blue: #2f80ed;
            --cortex-cyan: #39d0ff;
            --gridiron-green: #2f9e57;
            --gridiron-green-light: #4fc879;
            --gridiron-field: #1f5f38;
            --gridiron-field-dark: #163f28;
            --cortex-green: #2fd276;
            --cortex-yellow: #f2b84b;
            --cortex-red: #ef5b64;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: radial-gradient(circle at 72% 0%, rgba(47, 158, 87, 0.10), transparent 36%), linear-gradient(180deg, #08110d 0%, #09130f 100%);
            color: var(--cortex-text);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stMainBlockContainer"] { max-width: 1500px; padding-top: 1rem; padding-bottom: 2rem; }
        .block-container { padding-left: 1.7rem; padding-right: 1.7rem; }
        div[data-testid="stVerticalBlock"] { gap: 0.65rem; }
        h1, h2, h3, h4 { color: var(--cortex-text); letter-spacing: 0.01em; }
        h1 { font-size: 1.75rem !important; margin-bottom: 0.15rem !important; }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1.02rem !important; text-transform: uppercase; letter-spacing: 0.04em; }
        p, label, .stCaption { color: var(--cortex-muted); }

        section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0c1711 0%, #08110d 100%); border-right: 1px solid var(--cortex-border); }
        section[data-testid="stSidebar"] > div { padding-top: 0.65rem; }
        section[data-testid="stSidebar"] img { width: 100%; max-width: 100%; display: block; margin: 0 auto; object-fit: contain; }

        .stButton > button {
            min-height: 2.2rem; padding: 0.35rem 0.9rem; border-radius: 7px;
            border: 1px solid var(--cortex-border); background: var(--cortex-surface-2);
            color: var(--cortex-text); font-weight: 500; box-shadow: none;
            transition: border-color 0.18s ease, background-color 0.18s ease, color 0.18s ease, transform 0.18s ease;
        }
        .stButton > button:hover { border-color: var(--gridiron-green-light); color: var(--gridiron-green-light); background: #193024; transform: translateY(-1px); }
        .stButton > button[kind="primary"] { background: linear-gradient(90deg, var(--gridiron-field), var(--gridiron-green)); color: white; border: 1px solid var(--gridiron-green-light); }
        .stButton > button[kind="primary"]:hover { background: linear-gradient(90deg, var(--gridiron-green), var(--gridiron-green-light)); color: white; }

        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            background: var(--cortex-surface) !important;
            border-color: var(--cortex-border) !important;
            border-radius: 7px;
        }
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: var(--gridiron-green-light) !important;
            box-shadow: 0 0 0 1px rgba(79, 200, 121, 0.20);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] span {
            background: transparent !important; color: var(--cortex-text) !important; -webkit-text-fill-color: var(--cortex-text) !important;
        }
        [data-testid="stTextInput"] input:disabled,
        [data-testid="stTextArea"] textarea:disabled {
            background: transparent !important; color: var(--cortex-text) !important; -webkit-text-fill-color: var(--cortex-text) !important; opacity: 1 !important;
        }
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stTextInput"] div[data-baseweb="input"] > div,
        [data-testid="stTextArea"] div[data-baseweb="textarea"],
        [data-testid="stTextArea"] div[data-baseweb="textarea"] > div,
        [data-testid="stSelectbox"] div[data-baseweb="select"],
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"],
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
            background: var(--cortex-surface) !important;
        }
        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stMultiSelect"] label { color: var(--gridiron-green-light) !important; }

        [data-testid="stMultiSelect"] [data-baseweb="tag"] {
            background: var(--gridiron-field-dark) !important;
            border: 1px solid var(--cortex-border) !important;
            color: var(--cortex-text) !important;
        }
        [data-testid="stMultiSelect"] [data-baseweb="tag"] span,
        [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
            color: var(--cortex-text) !important;
            fill: var(--cortex-text) !important;
            -webkit-text-fill-color: var(--cortex-text) !important;
        }
        [data-testid="stMultiSelect"] input {
            color: var(--cortex-text) !important;
            -webkit-text-fill-color: var(--cortex-text) !important;
        }

        div[data-baseweb="popover"] ul, div[data-baseweb="menu"] { background: var(--cortex-surface-2) !important; }
        div[data-baseweb="popover"] li, div[data-baseweb="menu"] li { color: var(--cortex-text) !important; }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(21, 35, 27, 0.98), rgba(16, 26, 21, 0.98));
            border: 1px solid var(--cortex-border); border-radius: 9px; padding: 0.75rem 0.9rem;
            transition: border-color 0.18s ease, transform 0.18s ease;
        }
        div[data-testid="stMetric"]:hover { border-color: var(--gridiron-green); transform: translateY(-1px); }
        div[data-testid="stMetricLabel"] { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }
        div[data-testid="stMetricValue"] { font-size: 1.45rem; color: var(--cortex-text); }
        div[data-testid="stVerticalBlockBorderWrapper"] { background: var(--cortex-surface); border-color: var(--cortex-border) !important; border-radius: 9px; }

        button[data-baseweb="tab"] { height: 2.6rem; padding-left: 1rem; padding-right: 1rem; color: var(--cortex-muted); font-size: 0.9rem; }
        button[data-baseweb="tab"]:hover, button[data-baseweb="tab"][aria-selected="true"] { color: var(--gridiron-green-light); }
        div[data-baseweb="tab-highlight"] { background-color: var(--gridiron-green); }
        details { background: var(--cortex-surface); border: 1px solid var(--cortex-border) !important; border-radius: 8px; }
        hr { border-color: var(--cortex-border); margin: 0.8rem 0; }

        .cortex-brand-header { text-align: center; padding: 0.2rem 0 0.75rem; }
        .cortex-app-name { color: var(--cortex-text); font-size: 2rem; font-weight: 700; line-height: 1.1; letter-spacing: -0.025em; }
        .cortex-powered-label { color: var(--cortex-muted); font-size: 0.72rem; margin-top: 0.35rem; text-transform: uppercase; letter-spacing: 0.12em; }
        .cortex-engine-name { color: var(--cortex-cyan); font-size: 1rem; font-weight: 600; line-height: 1.25; }
        .cortex-online, .cortex-accent { color: var(--cortex-cyan); }
        .gridiron-accent { color: var(--gridiron-green-light); }
        .cortex-panel { border: 1px solid var(--cortex-border); border-radius: 9px; background: var(--cortex-surface); padding: 0.9rem 1rem; }
        .cortex-kicker { color: var(--gridiron-green-light); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
        .cortex-muted { color: var(--cortex-muted); }
        .gridiron-opportunity { color: var(--cortex-yellow); }
        .gridiron-positive { color: var(--cortex-green); }
        .gridiron-risk { color: var(--cortex-red); }
        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
