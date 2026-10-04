import streamlit as st
# ============================================================
# LIGHT / DARK THEME SELECTOR — TOP RIGHT
# ============================================================

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Dark"

if "theme_selector" not in st.session_state:
    st.session_state.theme_selector = st.session_state.app_theme


def update_theme():
    """Update the application theme."""
    st.session_state.app_theme = st.session_state.theme_selector


left_space, theme_column = st.columns([8, 2])

with theme_column:
    st.radio(
        "Appearance",
        options=["Light", "Dark"],
        horizontal=True,
        key="theme_selector",
        on_change=update_theme,
        label_visibility="visible",
    )


# ============================================================
# THEME COLORS
# ============================================================

if st.session_state.app_theme == "Dark":

    APP_BG = "#212121"
    APP_TEXT = "#F5F5F5"
    APP_SECONDARY = "#2D2D2D"
    APP_BORDER = "#454545"

    APP_INPUT_BG = "#303030"
    APP_BUTTON_BG = "#383838"
    APP_BUTTON_TEXT = "#F5F5F5"

    APP_ACCENT = "#6750E8"
    APP_SEND = "#F97316"

    APP_ALERT_BG = "#263746"
    APP_MUTED_TEXT = "#B5B5B5"

else:

    APP_BG = "#FFFFFF"
    APP_TEXT = "#262626"
    APP_SECONDARY = "#F7F7F8"
    APP_BORDER = "#D6D6D6"

    APP_INPUT_BG = "#FFFFFF"
    APP_BUTTON_BG = "#F7F7F8"
    APP_BUTTON_TEXT = "#262626"

    APP_ACCENT = "#5145E5"
    APP_SEND = "#F97316"

    APP_ALERT_BG = "#E5F3FF"
    APP_MUTED_TEXT = "#6B7280"


# ============================================================
# THEME-AWARE CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ========================================================
       THEME VARIABLES
    ======================================================== */

    :root {{
        --app-bg: {APP_BG};
        --app-text: {APP_TEXT};
        --app-secondary: {APP_SECONDARY};
        --app-border: {APP_BORDER};

        --app-input-bg: {APP_INPUT_BG};
        --app-button-bg: {APP_BUTTON_BG};
        --app-button-text: {APP_BUTTON_TEXT};

        --app-accent: {APP_ACCENT};
        --app-send: {APP_SEND};

        --app-alert-bg: {APP_ALERT_BG};
        --app-muted-text: {APP_MUTED_TEXT};
    }}


    /* ========================================================
       MAIN APP BACKGROUND
    ======================================================== */

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main {{
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
    }}

    [data-testid="stHeader"] {{
        background-color: var(--app-bg) !important;
    }}

    [data-testid="stToolbar"] {{
        background-color: transparent !important;
    }}

    .block-container {{
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }}


    /* ========================================================
       GENERAL TEXT
    ======================================================== */

    .stApp p,
    .stApp label,
    .stApp li,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {{
        color: var(--app-text);
    }}


    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        background-color: var(--app-secondary) !important;
        color: var(--app-text) !important;
    }}

    section[data-testid="stSidebar"] {{
        border-right: 1px solid var(--app-border) !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: var(--app-text);
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: var(--app-border) !important;
    }}


    /* ========================================================
       TOP-RIGHT THEME SELECTOR
    ======================================================== */

    [data-testid="stRadio"] {{
        background: transparent !important;
    }}

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p {{
        color: var(--app-text) !important;
    }}

    [data-testid="stRadio"] [role="radiogroup"] {{
        gap: 0.5rem;
        justify-content: flex-end;
    }}

    [data-testid="stRadio"] [role="radio"] {{
        color: var(--app-text) !important;
    }}


    /* ========================================================
       HEADER
    ======================================================== */

    .main-header {{
        width: 100%;
        text-align: center;
        padding: 12px 10px 32px;
        box-sizing: border-box;
        background: transparent !important;
    }}

    .header-title-row {{
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: wrap;
        gap: 10px;
    }}

    .main-header .main-title {{
        margin: 0;
        color: var(--app-text) !important;
        font-size: clamp(1.5rem, 2.7vw, 2.2rem);
        font-weight: 700;
        letter-spacing: -1px;
        line-height: 1.35;
    }}

    .main-header .header-author {{
        color: var(--app-muted-text) !important;
        font-size: 0.9rem;
        font-weight: 500;
        white-space: nowrap;
    }}

    .main-header .header-subtitle {{
        margin: 12px 0 0;
        color: var(--app-muted-text) !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }}


    /* ========================================================
       CHAT MESSAGES
    ======================================================== */

    [data-testid="stChatMessage"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--app-text) !important;
        padding: 0.8rem 0.25rem;
    }}

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] span {{
        color: var(--app-text) !important;
        line-height: 1.75;
    }}


    /* ========================================================
       CHAT INPUT
    ======================================================== */

    [data-testid="stChatInput"] {{
        background: var(--app-input-bg) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 24px !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"]:focus-within {{
        border: 1px solid var(--app-accent) !important;
        box-shadow: 0 0 0 1px var(--app-accent) !important;
    }}

    [data-testid="stChatInput"] > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: var(--app-text) !important;
        caret-color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: var(--app-muted-text) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: var(--app-muted-text) !important;
    }}


    /* ========================================================
       ORANGE CHAT SEND BUTTON
    ======================================================== */

    [data-testid="stChatInput"] button,
    [data-testid="stChatInput"] button[kind],
    [data-testid="stChatInput"] button:disabled,
    [data-testid="stChatInput"] button[disabled] {{
        background-color: var(--app-send) !important;
        background: var(--app-send) !important;

        color: #FFFFFF !important;
        border: 1px solid var(--app-send) !important;
        border-radius: 50% !important;

        opacity: 1 !important;
        box-shadow: none !important;
        filter: none !important;
    }}

    [data-testid="stChatInput"] button svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatInput"] button:hover {{
        background-color: #EA580C !important;
        border-color: #EA580C !important;
        filter: none !important;
    }}

    [data-testid="stChatInput"] button:disabled {{
        background-color: var(--app-send) !important;
        border-color: var(--app-send) !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }}


    /* ========================================================
       GENERAL BUTTONS
    ======================================================== */

    .stButton > button {{
        background-color: var(--app-button-bg) !important;
        color: var(--app-button-text) !important;

        border: 1px solid var(--app-border) !important;
        border-radius: 10px !important;

        min-height: 2.5rem;
        font-weight: 500;
        box-shadow: none !important;
    }}

    .stButton > button:hover {{
        background-color: var(--app-secondary) !important;
        border-color: var(--app-accent) !important;
        color: var(--app-text) !important;
    }}


    /* ========================================================
       PRIMARY BUTTONS
    ======================================================== */

    .stButton > button[kind="primary"] {{
        background-color: var(--app-accent) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--app-accent) !important;
    }}

    .stButton > button[kind="primary"] *,
    .stButton > button[kind="primary"]:hover {{
        color: #FFFFFF !important;
    }}


    /* ========================================================
       TEXT INPUTS AND TEXT AREAS
    ======================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {{
        background-color: var(--app-input-bg) !important;
        color: var(--app-text) !important;
        border-color: var(--app-border) !important;
        caret-color: var(--app-text) !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: var(--app-muted-text) !important;
        opacity: 1 !important;
    }}


    /* ========================================================
       SELECT BOXES
    ======================================================== */

    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] {{
        background-color: var(--app-input-bg) !important;
        color: var(--app-text) !important;
        border-color: var(--app-border) !important;
    }}


    /* ========================================================
       EXPANDERS
    ======================================================== */

    [data-testid="stExpander"] {{
        background-color: var(--app-secondary) !important;
        color: var(--app-text) !important;

        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] label,
    [data-testid="stExpander"] span {{
        color: var(--app-text) !important;
    }}

    [data-testid="stExpander"] pre,
    [data-testid="stExpander"] code {{
        color: var(--app-text) !important;
        background-color: var(--app-secondary) !important;
    }}


    /* ========================================================
       ALERTS
    ======================================================== */

    [data-testid="stAlert"] {{
        background-color: var(--app-alert-bg) !important;
        color: var(--app-text) !important;

        border: 1px solid var(--app-border) !important;
        border-radius: 10px !important;
    }}

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {{
        color: var(--app-text) !important;
    }}


    /* ========================================================
       DIVIDERS
    ======================================================== */

    hr {{
        border: none !important;
        border-top: 1px solid var(--app-border) !important;
        opacity: 1 !important;
    }}


    /* ========================================================
       CAPTIONS
    ======================================================== */

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: var(--app-muted-text) !important;
        opacity: 1 !important;
    }}


      /* ========================================================
       RESPONSIVE
    ======================================================== */

    @media (max-width: 768px) {{

        .block-container {{
            padding-top: 1rem;
        }}

        .header-title-row {{
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }}

        .main-header .main-title {{
            font-size: 1.5rem;
        }}

        .main-header .header-author {{
            font-size: 0.85rem;
        }}

    }}


    
        /* ========================================================
       THEME-AWARE DOCUMENT UPLOADER
    ======================================================== */

    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > section,
    [data-testid="stFileUploader"] section {{
        background-color: var(--app-input-bg) !important;
        color: var(--app-text) !important;
        border-color: var(--app-border) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}

    [data-testid="stFileUploader"] section * {{
        color: var(--app-text) !important;
    }}

    [data-testid="stFileUploader"] small {{
        color: var(--app-muted-text) !important;
    }}

    [data-testid="stFileUploader"] button {{
        background-color: var(--app-button-bg) !important;
        color: var(--app-button-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }}

    [data-testid="stFileUploader"] button:hover {{
        background-color: var(--app-secondary) !important;
        border-color: var(--app-accent) !important;
        color: var(--app-text) !important;
    }}


    /* ========================================================
       FIXED BOTTOM CHAT AREA — LIGHT / DARK THEME
    ======================================================== */

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div,
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div {{
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
        box-shadow: none !important;
    }}

    [data-testid="stBottom"] {{
        border-top: 1px solid var(--app-border) !important;
    }}

    [data-testid="stBottom"]::before,
    [data-testid="stBottom"]::after {{
        background: var(--app-bg) !important;
    }}

    [data-testid="stBottomBlockContainer"] {{
        padding-top: 0.75rem !important;
        padding-bottom: 1rem !important;
    }}


    /* ========================================================
       CHAT INPUT — THEME-AWARE
    ======================================================== */

    [data-testid="stChatInput"] {{
        background-color: var(--app-input-bg) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 20px !important;
        box-shadow: none !important;
        overflow: visible !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stChatInput"]:focus-within {{
        border-color: var(--app-accent) !important;
        box-shadow: 0 0 0 1px var(--app-accent) !important;
    }}

    [data-testid="stChatInput"] > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: var(--app-text) !important;
        caret-color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border: none !important;
        box-shadow: none !important;
        padding: 12px 16px !important;
        line-height: 1.5 !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: var(--app-muted-text) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: var(--app-muted-text) !important;
    }}


    /* ========================================================
       ORANGE SEND BUTTON
    ======================================================== */

    [data-testid="stChatInput"] button,
    [data-testid="stChatInput"] button:disabled,
    [data-testid="stChatInput"] button[disabled] {{
        background-color: var(--app-send) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--app-send) !important;
        border-radius: 50% !important;
        opacity: 1 !important;
        box-shadow: none !important;
        filter: none !important;
    }}

    [data-testid="stChatInput"] button svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatInput"] button:hover {{
        background-color: #EA580C !important;
        border-color: #EA580C !important;
    }}


    /* ========================================================
       FOOTER — THEME-AWARE
    ======================================================== */

    footer,
    [data-testid="stFooter"] {{
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
    }}

    [data-testid="stFooter"] *,
    footer * {{
        color: var(--app-text) !important;
    }}


    /* ========================================================
       RESPONSIVE CHAT INPUT
    ======================================================== */

    @media (max-width: 768px) {{
        [data-testid="stBottomBlockContainer"] {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}

        [data-testid="stChatInput"] {{
            border-radius: 16px !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)