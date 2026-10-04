import streamlit as st


def apply_theme():

    """Apply the Multimodal RAG visual theme. UI styling only."""

    st.markdown(
        """
        <style>

        /* =====================================================
           ROOT VARIABLES
        ===================================================== */

        :root {

            --rag-bg: #171126;
            --rag-bg-secondary: #211638;

            --rag-card: rgba(255, 255, 255, 0.08);
            --rag-card-hover: rgba(255, 255, 255, 0.12);

            --rag-border: rgba(255, 255, 255, 0.14);

            --rag-purple: #8B5CF6;
            --rag-purple-light: #A78BFA;

            --rag-text: #F8F7FF;
            --rag-muted: #B8B2C9;

            --rag-input: rgba(255, 255, 255, 0.09);
        }


        /* =====================================================
           MAIN APPLICATION BACKGROUND
        ===================================================== */

        .stApp {

            background:

                radial-gradient(
                    circle at 15% 10%,
                    rgba(139, 92, 246, 0.20),
                    transparent 32%
                ),

                radial-gradient(
                    circle at 85% 20%,
                    rgba(124, 58, 237, 0.16),
                    transparent 30%
                ),

                linear-gradient(
                    135deg,
                    #120D21 0%,
                    #1A1230 45%,
                    #120D21 100%
                );

            color: var(--rag-text);
        }


        /* =====================================================
           MAIN CONTENT
        ===================================================== */

        .block-container {

            max-width: 1200px;

            padding-top: 2rem;

            padding-bottom: 4rem;
        }


        /* =====================================================
           HEADER
        ===================================================== */

        .rag-header {

            padding: 18px 10px 30px;
        }


        .rag-header-title {

            font-size: 2.1rem;

            font-weight: 750;

            letter-spacing: -0.8px;

            margin: 0;

            color: var(--rag-text);
        }


        .rag-header-subtitle {

            margin-top: 8px;

            color: var(--rag-muted);

            font-size: 0.98rem;
        }


        /* =====================================================
           GLASS CARD
        ===================================================== */

        .rag-card {

            background: var(--rag-card);

            border:
                1px solid var(--rag-border);

            border-radius: 22px;

            padding: 20px;

            backdrop-filter: blur(18px);

            -webkit-backdrop-filter: blur(18px);

            box-shadow:
                0 18px 50px rgba(0, 0, 0, 0.20);
        }


        /* =====================================================
           CHAT MESSAGE — BASE
        ===================================================== */

        [data-testid="stChatMessage"] {

            position: relative !important;

            background:
                rgba(255, 255, 255, 0.035) !important;

            border:
                1px solid rgba(167, 139, 250, 0.12) !important;

            border-radius: 18px !important;

            padding: 1rem 1.1rem !important;

            margin:
                0.55rem 0 0.9rem 0 !important;

            box-shadow:
                0 8px 24px rgba(0, 0, 0, 0.12) !important;

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease,
                transform 0.2s ease !important;
        }


        /* =====================================================
           USER MESSAGE
        ===================================================== */

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        ) {

            max-width: 78% !important;

            margin-left: auto !important;

            margin-right: 0 !important;

            background:
                linear-gradient(
                    135deg,
                    rgba(139, 92, 246, 0.24),
                    rgba(109, 40, 217, 0.16)
                ) !important;

            border:
                1px solid rgba(167, 139, 250, 0.30) !important;

            border-radius:
                18px 18px 6px 18px !important;

            box-shadow:
                0 8px 26px rgba(76, 29, 149, 0.16) !important;
        }


        /* =====================================================
           NEXUS AI MESSAGE
        ===================================================== */

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-assistant"]
        ) {

            max-width: 94% !important;

            margin-left: 0 !important;

            margin-right: auto !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.065),
                    rgba(139, 92, 246, 0.045)
                ) !important;

            border:
                1px solid rgba(167, 139, 250, 0.17) !important;

            border-radius:
                18px 18px 18px 6px !important;

            box-shadow:
                0 10px 30px rgba(0, 0, 0, 0.15) !important;
        }


        /* =====================================================
           MESSAGE HOVER
        ===================================================== */

        [data-testid="stChatMessage"]:hover {

            border-color:
                rgba(167, 139, 250, 0.28) !important;

            box-shadow:
                0 12px 32px rgba(0, 0, 0, 0.18) !important;

            transform: translateY(-1px);
        }


        /* =====================================================
           CHAT TEXT
        ===================================================== */

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li {

            color: var(--rag-text) !important;

            line-height: 1.72 !important;
        }


        [data-testid="stChatMessage"] p:last-child {

            margin-bottom: 0 !important;
        }


        /* =====================================================
           RESPONSE HEADINGS
        ===================================================== */

        [data-testid="stChatMessage"] h1,
        [data-testid="stChatMessage"] h2,
        [data-testid="stChatMessage"] h3,
        [data-testid="stChatMessage"] h4 {

            color: var(--rag-text) !important;

            letter-spacing: -0.2px !important;

            margin-top: 0.8rem !important;

            margin-bottom: 0.45rem !important;
        }


        /* =====================================================
           CHAT AVATARS
        ===================================================== */

        [data-testid="stChatMessage"]
        [data-testid^="chatAvatarIcon"] {

            border-radius: 12px !important;

            border:
                1px solid rgba(167, 139, 250, 0.25) !important;

            box-shadow:
                0 4px 14px rgba(0, 0, 0, 0.16) !important;
        }


        /* =====================================================
           NEXUS AI AVATAR
        ===================================================== */

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-assistant"]
        )
        [data-testid^="chatAvatarIcon"] {

            background:
                linear-gradient(
                    135deg,
                    #8B5CF6,
                    #6D28D9
                ) !important;
        }


        /* =====================================================
           USER AVATAR
        ===================================================== */

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        )
        [data-testid^="chatAvatarIcon"] {

            background:
                rgba(167, 139, 250, 0.22) !important;
        }


        /* =====================================================
           INLINE CODE
        ===================================================== */

        [data-testid="stChatMessage"] code {

            background:
                rgba(139, 92, 246, 0.14) !important;

            color: #DDD6FE !important;

            border-radius: 6px !important;

            padding: 0.15rem 0.35rem !important;
        }


        /* =====================================================
           CODE BLOCKS
        ===================================================== */

        [data-testid="stChatMessage"] pre {

            background:
                rgba(8, 6, 18, 0.82) !important;

            border:
                1px solid rgba(167, 139, 250, 0.16) !important;

            border-radius: 12px !important;

            padding: 1rem !important;

            margin-top: 0.8rem !important;

            margin-bottom: 0.8rem !important;

            overflow-x: auto !important;
        }


        /* =====================================================
           LINKS
        ===================================================== */

        [data-testid="stChatMessage"] a {

            color: #C4B5FD !important;

            text-decoration-color:
                rgba(196, 181, 253, 0.35) !important;
        }


        /* =====================================================
           MOBILE CHAT
        ===================================================== */

        @media (max-width: 768px) {

            [data-testid="stChatMessage"] {

                max-width: 96% !important;

                padding:
                    0.85rem 0.9rem !important;

                border-radius: 15px !important;
            }


            [data-testid="stChatMessage"]:has(
                [data-testid="chatAvatarIcon-user"]
            ) {

                max-width: 88% !important;

                margin-left: auto !important;
            }


            [data-testid="stChatMessage"]:has(
                [data-testid="chatAvatarIcon-assistant"]
            ) {

                max-width: 96% !important;

                margin-right: auto !important;
            }


            [data-testid="stChatMessage"] pre {

                padding: 0.8rem !important;
            }
        }


        /* =====================================================
           CHAT INPUT OUTER SURFACE
        ===================================================== */

        .stChatFloatingInputContainer {

            background: transparent !important;

            background-color: transparent !important;

            padding-left: 0 !important;

            padding-right: 0 !important;

            margin-left: 0 !important;

            margin-right: 0 !important;

            box-shadow: none !important;
        }


        /* =====================================================
           CHAT INPUT OUTER CHILD
        ===================================================== */

        .stChatFloatingInputContainer > div {

            background: transparent !important;

            background-color: transparent !important;

            width: 100% !important;

            max-width: none !important;

            padding-left: 0 !important;

            padding-right: 0 !important;

            margin-left: 0 !important;

            margin-right: 0 !important;

            box-shadow: none !important;
        }


        /* =====================================================
           CHAT INPUT
        ===================================================== */

        [data-testid="stChatInput"] {

            background:
                var(--rag-input) !important;

            background-color:
                var(--rag-input) !important;

            border:
                1px solid rgba(167, 139, 250, 0.65) !important;

            border-radius: 999px !important;

            width: 100% !important;

            max-width: none !important;

            margin-left: 0 !important;

            margin-right: 0 !important;

            padding: 0 !important;

            overflow: hidden !important;

            backdrop-filter: blur(18px);

            -webkit-backdrop-filter: blur(18px);

            box-shadow:
                0 0 0 1px rgba(167, 139, 250, 0.12),
                0 10px 35px rgba(0, 0, 0, 0.25) !important;
        }


        /* =====================================================
           CHAT INPUT PARENT
        ===================================================== */

        section[data-testid="stMain"] > div:has(
            [data-testid="stChatInput"]
        ) {

            background: transparent !important;

            background-color: transparent !important;

            padding-left: 0 !important;

            padding-right: 0 !important;

            box-shadow: none !important;
        }


        /* =====================================================
           CHAT INPUT INNER LAYERS
        ===================================================== */

        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] form,
        [data-testid="stChatInput"] form > div {

            background: transparent !important;

            background-color: transparent !important;

            border: none !important;

            box-shadow: none !important;
        }


        /* =====================================================
           CHAT TEXTAREA
        ===================================================== */

        [data-testid="stChatInput"] textarea {

            background: transparent !important;

            color: var(--rag-text) !important;

            -webkit-text-fill-color:
                var(--rag-text) !important;

            border: none !important;

            box-shadow: none !important;

            outline: none !important;
        }


        [data-testid="stChatInput"] textarea::placeholder {

            color: var(--rag-muted) !important;

            -webkit-text-fill-color:
                var(--rag-muted) !important;
        }


        /* =====================================================
           CHAT SEND BUTTON
        ===================================================== */

        [data-testid="stChatInput"] button {

            background:
                linear-gradient(
                    135deg,
                    #8B5CF6,
                    #6D28D9
                ) !important;

            border: none !important;

            border-radius: 50% !important;

            color: white !important;

            box-shadow:
                0 8px 22px rgba(124, 58, 237, 0.35) !important;
        }


        [data-testid="stChatInput"] button svg {

            color: white !important;

            fill: white !important;

            stroke: white !important;
        }
        /* =====================================================
   NEXUS AI — EMPTY CHAT STATE
===================================================== */

.nexus-empty-state {

    width: min(760px, 92%);

     margin: 13px auto 45px auto;

    padding: 38px 34px;


    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(139, 92, 246, 0.09),
            rgba(255, 255, 255, 0.035)
        );

    border:
        1px solid rgba(167, 139, 250, 0.14);

    border-radius: 26px;

    backdrop-filter: blur(16px);

    -webkit-backdrop-filter: blur(16px);

    box-shadow:
        0 20px 55px rgba(0, 0, 0, 0.12);

    box-sizing: border-box;
}


/* -----------------------------------------------------
   ICON
----------------------------------------------------- */

.nexus-empty-icon {

    width: 58px;

    height: 58px;

    margin:
        0 auto 18px auto;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #8B5CF6,
            #6D28D9
        );

    color: white;

    font-size: 1.65rem;

    font-weight: 700;

    box-shadow:
        0 12px 30px rgba(124, 58, 237, 0.28);
}


/* -----------------------------------------------------
   TITLE
----------------------------------------------------- */

.nexus-empty-state h2 {

    margin:
        0 0 8px 0;

    color:
        #F8F7FF;

    font-size:
        1.65rem;

    font-weight:
        700;

    letter-spacing:
        -0.4px;
}


/* -----------------------------------------------------
   DESCRIPTION
----------------------------------------------------- */

.nexus-empty-description {

    margin:
        0;

    color:
        #C4B5FD;

    font-size:
        1rem;

    font-weight:
        550;
}


/* -----------------------------------------------------
   HELPER TEXT
----------------------------------------------------- */

.nexus-empty-helper {

    max-width:
        570px;

    margin:
        12px auto 28px auto;

    color:
        #AFA8BF;

    font-size:
        0.92rem;

    line-height:
        1.65;
}


/* -----------------------------------------------------
   FEATURE CARDS
----------------------------------------------------- */

.nexus-empty-cards {

    display:
        flex;

    justify-content:
        center;

    gap:
        14px;

    width:
        100%;
}


/* -----------------------------------------------------
   INDIVIDUAL CARD
----------------------------------------------------- */

.nexus-empty-card {

    flex:
        1 1 0;

    max-width:
        300px;

    display:
        flex;

    align-items:
        center;

    gap:
        13px;

    text-align:
        left;

    padding:
        15px 17px;

    background:
        rgba(255, 255, 255, 0.045);

    border:
        1px solid rgba(167, 139, 250, 0.14);

    border-radius:
        15px;

    box-sizing:
        border-box;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        transform 0.2s ease;
}


.nexus-empty-card:hover {

    background:
        rgba(139, 92, 246, 0.09);

    border-color:
        rgba(167, 139, 250, 0.28);

    transform:
        translateY(-2px);
}


/* -----------------------------------------------------
   CARD ICON
----------------------------------------------------- */

.nexus-empty-card-icon {

    width:
        38px;

    height:
        38px;

    flex:
        0 0 38px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        11px;

    background:
        rgba(139, 92, 246, 0.14);

    font-size:
        1.05rem;
}


/* -----------------------------------------------------
   CARD TEXT
----------------------------------------------------- */

.nexus-empty-card strong {

    display:
        block;

    margin-bottom:
        3px;

    color:
        #F8F7FF;

    font-size:
        0.86rem;

    font-weight:
        650;
}


.nexus-empty-card span {

    display:
        block;

    color:
        #AFA8BF;

    font-size:
        0.74rem;

    line-height:
        1.45;
}


/* =====================================================
   EMPTY STATE — MOBILE
===================================================== */

@media (max-width: 768px) {

    .nexus-empty-state {

        width:
            94%;

        margin:
            70px auto 100px auto;

        padding:
            30px 20px;
    }


    .nexus-empty-state h2 {

        font-size:
            1.35rem;
    }


    .nexus-empty-cards {

        flex-direction:
            column;
    }


    .nexus-empty-card {

        max-width:
            none;

        width:
            100%;
    }
}


        /* =====================================================
           SIDEBAR
        ===================================================== */


        /* -----------------------------------------------------
           SIDEBAR OUTER FRAME
        ----------------------------------------------------- */

        section[data-testid="stSidebar"] {

            position: relative !important;

            width: 320px !important;

            min-width: 320px !important;

            max-width: 320px !important;

            flex: 0 0 320px !important;

            height: 100vh !important;

            min-height: 100vh !important;

            max-height: 100vh !important;

            overflow: hidden !important;

            background:

                radial-gradient(
                    circle at 20% 10%,
                    rgba(139, 92, 246, 0.16),
                    transparent 32%
                ),

                linear-gradient(
                    180deg,
                    #171126 0%,
                    #211638 100%
                ) !important;

            border-right:
                1px solid rgba(167, 139, 250, 0.16) !important;

            box-shadow:
                10px 0 40px rgba(0, 0, 0, 0.12);

            box-sizing: border-box !important;
        }


        section[data-testid="stSidebar"] * {

            color: var(--rag-text);
        }


        /* -----------------------------------------------------
           SIDEBAR CONTENT
           NATIVE STREAMLIT SCROLL CONTAINER
        ----------------------------------------------------- */

        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"] {

            position: relative !important;

            display: flex !important;

            flex-direction: column !important;

            width: 100% !important;

            height: 100vh !important;

            min-height: 100vh !important;

            max-height: 100vh !important;

            overflow-y: auto !important;

            overflow-x: hidden !important;

            box-sizing: border-box !important;

            scrollbar-width: thin;

            scrollbar-color:
                rgba(167, 139, 250, 0.55)
                transparent;
        }


        /* -----------------------------------------------------
           SIDEBAR SCROLLBAR
        ----------------------------------------------------- */

        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"]::-webkit-scrollbar {

            width: 8px;
        }


        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"]::-webkit-scrollbar-track {

            background: transparent;
        }


        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {

            background:
                rgba(167, 139, 250, 0.50);

            border-radius: 10px;
        }


        section[data-testid="stSidebar"]
        [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb:hover {

            background:
                rgba(167, 139, 250, 0.75);
        }


        /* -----------------------------------------------------
           SIDEBAR HEADER
        ----------------------------------------------------- */

        section[data-testid="stSidebar"]
        [data-testid="stSidebarHeader"] {

            flex: 0 0 auto !important;

            width: 100% !important;

            box-sizing: border-box !important;
        }


        /* -----------------------------------------------------
           SIDEBAR USER CONTENT
           
           IMPORTANT:
           Do not create a second scrollbar here.
        ----------------------------------------------------- */

        section[data-testid="stSidebar"]
        [data-testid="stSidebarUserContent"] {

            position: relative !important;

            display: block !important;

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            overflow: visible !important;

            flex: 0 0 auto !important;

            box-sizing: border-box !important;
        }


        /* -----------------------------------------------------
           SIDEBAR USER CONTENT DIRECT CHILD
        ----------------------------------------------------- */

        section[data-testid="stSidebar"]
        [data-testid="stSidebarUserContent"]
        > div {

            position: relative !important;

            display: block !important;

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            overflow: visible !important;

            box-sizing: border-box !important;
        }


        /* -----------------------------------------------------
           MAIN SIDEBAR CONTAINER
           
           IMPORTANT:
           No height.
           No max-height.
           No overflow.
           
           The native Streamlit sidebar content handles
           scrolling.
        ----------------------------------------------------- */

        .st-key-sidebar_scroll_content {

            position: relative !important;

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            overflow: visible !important;

            box-sizing: border-box !important;

            padding-right: 4px !important;

            padding-bottom: 12px !important;
        }


        .st-key-sidebar_scroll_content > div {

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            overflow: visible !important;

            box-sizing: border-box !important;
        }


        /* =====================================================
           GENERAL BUTTONS
        ===================================================== */

        .stButton > button {

            background:
                var(--rag-card) !important;

            color:
                var(--rag-text) !important;

            border:
                1px solid var(--rag-border) !important;

            border-radius: 12px !important;

            min-height: 2.5rem;

            transition:
                transform 0.15s ease,
                background 0.15s ease,
                border-color 0.15s ease;

            box-sizing: border-box !important;
        }


        .stButton > button:hover {

            background:
                var(--rag-card-hover) !important;

            border-color:
                rgba(167, 139, 250, 0.55) !important;

            transform: translateY(-1px);
        }


        /* =====================================================
           PRIMARY BUTTON
        ===================================================== */

        .stButton > button[kind="primary"] {

            background:
                linear-gradient(
                    135deg,
                    #9B6CFF,
                    #7C3AED
                ) !important;

            border:
                1px solid rgba(196, 181, 253, 0.35) !important;

            border-radius: 14px !important;

            color: white !important;

            min-height: 2.65rem;

            box-shadow:
                0 8px 24px rgba(124, 58, 237, 0.25);

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease,
                filter 0.15s ease;
        }


        .stButton > button[kind="primary"]:hover {

            filter: brightness(1.08);

            box-shadow:
                0 10px 28px rgba(124, 58, 237, 0.35);

            transform: translateY(-1px);
        }


        /* =====================================================
           ADD TO KNOWLEDGE BASE
        ===================================================== */

        .st-key-index_documents_button {

            position: relative !important;

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            overflow: visible !important;

            margin-top: 20px !important;

            margin-bottom: 20px !important;

            box-sizing: border-box !important;
        }


        .st-key-index_documents_button button {

            width: 100% !important;

            background:
                linear-gradient(
                    135deg,
                    rgba(139, 92, 246, 0.22),
                    rgba(109, 40, 217, 0.18)
                ) !important;

            color:
                #F8F7FF !important;

            border:
                1px solid rgba(167, 139, 250, 0.38) !important;

            border-radius: 14px !important;

            min-height: 2.6rem;

            box-shadow:
                0 6px 20px rgba(124, 58, 237, 0.12);

            transition:
                transform 0.15s ease,
                background 0.15s ease,
                border-color 0.15s ease,
                box-shadow 0.15s ease;

            box-sizing: border-box !important;
        }


        .st-key-index_documents_button button:hover {

            background:
                linear-gradient(
                    135deg,
                    rgba(139, 92, 246, 0.34),
                    rgba(109, 40, 217, 0.28)
                ) !important;

            border-color:
                rgba(167, 139, 250, 0.65) !important;

            box-shadow:
                0 8px 24px rgba(124, 58, 237, 0.22);

            transform: translateY(-1px);
        }


        /* =====================================================
           EXPANDERS
        ===================================================== */

        [data-testid="stExpander"] {

            background:
                var(--rag-card) !important;

            border:
                1px solid var(--rag-border) !important;

            border-radius: 16px !important;

            box-sizing: border-box !important;
        }


        /* =====================================================
           FILE UPLOADER
           
           IMPORTANT:
           We intentionally do NOT force a height here.
           
           Streamlit controls the internal uploader layout.
           We only style the outer surface.
        ===================================================== */

        .st-key-sidebar_scroll_content
        [data-testid="stFileUploader"] {

            width: 100% !important;

            max-width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            margin: 0 !important;

            padding: 0 !important;

            box-sizing: border-box !important;

            overflow: visible !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(139, 92, 246, 0.13),
                    rgba(255, 255, 255, 0.05)
                ) !important;

            border:
                1px solid rgba(167, 139, 250, 0.25) !important;

            border-radius: 18px !important;

            backdrop-filter: blur(14px);

            -webkit-backdrop-filter: blur(14px);

            box-shadow:
                0 10px 30px rgba(0, 0, 0, 0.16);

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }


        /* -----------------------------------------------------
           FILE UPLOADER HOVER
        ----------------------------------------------------- */

        .st-key-sidebar_scroll_content
        [data-testid="stFileUploader"]:hover {

            border-color:
                rgba(167, 139, 250, 0.50) !important;

            box-shadow:
                0 12px 34px rgba(124, 58, 237, 0.16);
        }


        /* -----------------------------------------------------
           FILE UPLOADER INTERNAL SECTION
           
           Do not assign a fixed height.
        ----------------------------------------------------- */

        .st-key-sidebar_scroll_content
        [data-testid="stFileUploader"] section {

            background: transparent !important;

            border: none !important;

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            margin: 0 !important;

            box-sizing: border-box !important;
        }


        /* -----------------------------------------------------
           FILE UPLOADER INTERNAL BLOCKS
        ----------------------------------------------------- */

        .st-key-sidebar_scroll_content
        [data-testid="stFileUploader"] section > div {

            width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            max-height: none !important;

            box-sizing: border-box !important;
        }


        /* =====================================================
   SIDEBAR DEVELOPER SETTINGS
===================================================== */

.st-key-sidebar_scroll_content
[data-testid="stExpander"] {

    width: 100% !important;

    margin-top: 6px !important;

    margin-bottom: 10px !important;

    box-sizing: border-box !important;
}


/* =====================================================
   SIDEBAR CLEAR CONVERSATION
===================================================== */

.st-key-sidebar_scroll_content
.stButton {

    width: 100% !important;

    box-sizing: border-box !important;
}


.st-key-sidebar_scroll_content
.stButton > button {

    width: 100% !important;

    box-sizing: border-box !important;
}

        /* -----------------------------------------------------
           DEVELOPER SETTINGS
        ----------------------------------------------------- */

        .st-key-sidebar_bottom_controls
        [data-testid="stExpander"] {

            width: 100% !important;

            margin:
                0 0 6px 0 !important;

            background:
                rgba(255, 255, 255, 0.07) !important;

            border:
                1px solid rgba(255, 255, 255, 0.14) !important;

            border-radius: 14px !important;

            box-shadow:
                0 8px 24px rgba(0, 0, 0, 0.22) !important;

            box-sizing: border-box !important;
        }


        .st-key-sidebar_bottom_controls
        [data-testid="stExpanderDetails"] {

            box-sizing: border-box !important;

            overflow: hidden !important;
        }


        /* -----------------------------------------------------
           BOTTOM CONTROL BUTTONS
        ----------------------------------------------------- */

        .st-key-sidebar_bottom_controls
        .stButton {

            width: 100% !important;

            margin: 0 !important;
        }


        .st-key-sidebar_bottom_controls
        .stButton > button {

            width: 100% !important;

            min-height: 2.35rem !important;

            margin: 0 !important;

            border-radius: 12px !important;

            box-sizing: border-box !important;
        }


        /* =====================================================
           ALERTS
        ===================================================== */

        [data-testid="stAlert"] {

            border-radius: 14px !important;

            border:
                1px solid var(--rag-border) !important;
        }


        /* =====================================================
           DIVIDERS
        ===================================================== */

        hr {

            border-color:
                var(--rag-border);
        }


        /* =====================================================
           CHAT BOTTOM AREA
        ===================================================== */

        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {

            background: transparent !important;

            background-color: transparent !important;

            box-shadow: none !important;

            border: none !important;
        }


        [data-testid="stBottom"] > div {

            background: transparent !important;

            background-color: transparent !important;
        }


        /* =====================================================
           STREAMLIT APP CONTAINER
        ===================================================== */

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {

            background: transparent !important;

            background-color: transparent !important;
        }


        /* =====================================================
           MOBILE
        ===================================================== */

        @media (max-width: 768px) {

            .block-container {

                padding-top: 1rem;
            }


            .rag-header-title {

                font-size: 1.55rem;
            }


            .rag-card {

                border-radius: 16px;

                padding: 15px;
            }


            section[data-testid="stSidebar"] {

                width: 320px !important;

                min-width: 320px !important;

                height: 100vh !important;

                min-height: 100vh !important;
            }


            .st-key-sidebar_bottom_controls {

                padding-left:
                    12px !important;

                padding-right:
                    12px !important;

                padding-bottom:
                    12px !important;
            }


            .st-key-sidebar_scroll_content {

                padding-bottom:
                    12px !important;
            }
        }
        /* =====================================================
   FILE UPLOADER LABEL POSITION
===================================================== */

.st-key-sidebar_scroll_content
[data-testid="stFileUploader"] label {

    padding-left: 12px !important;

    box-sizing: border-box !important;
}
/* =====================================================
   NEXUS AI — CONVERSATION MESSAGE POLISH
===================================================== */

/* Message spacing */
[data-testid="stChatMessage"] {
    margin-top: 10px !important;
    margin-bottom: 16px !important;
    padding: 16px 18px !important;
}


/* -----------------------------------------------------
   USER MESSAGE
----------------------------------------------------- */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {

    max-width: 78% !important;

    margin-left: auto !important;
    margin-right: 0 !important;

    background:
        linear-gradient(
            135deg,
            rgba(139, 92, 246, 0.26),
            rgba(109, 40, 217, 0.16)
        ) !important;

    border:
        1px solid rgba(167, 139, 250, 0.32) !important;

    border-radius:
        20px 20px 6px 20px !important;

    box-shadow:
        0 8px 28px rgba(76, 29, 149, 0.18) !important;
}


/* -----------------------------------------------------
   NEXUS AI MESSAGE
----------------------------------------------------- */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {

    max-width: 92% !important;

    margin-left: 0 !important;
    margin-right: auto !important;

    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.065),
            rgba(139, 92, 246, 0.045)
        ) !important;

    border:
        1px solid rgba(167, 139, 250, 0.18) !important;

    border-radius:
        20px 20px 20px 6px !important;

    box-shadow:
        0 10px 32px rgba(0, 0, 0, 0.16) !important;
}


/* -----------------------------------------------------
   MESSAGE TEXT
----------------------------------------------------- */

[data-testid="stChatMessage"] p {

    font-size: 0.96rem !important;

    line-height: 1.72 !important;

    color: #F8F7FF !important;
}


/* -----------------------------------------------------
   AI HEADINGS
----------------------------------------------------- */

[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {

    color: #F8F7FF !important;

    margin-top: 12px !important;

    margin-bottom: 7px !important;
}


/* -----------------------------------------------------
   AI LISTS
----------------------------------------------------- */

[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] ol {

    padding-left: 24px !important;

    margin-top: 8px !important;

    margin-bottom: 8px !important;
}


/* -----------------------------------------------------
   CODE BLOCKS
----------------------------------------------------- */

[data-testid="stChatMessage"] pre {

    background:
        rgba(7, 5, 16, 0.82) !important;

    border:
        1px solid rgba(167, 139, 250, 0.18) !important;

    border-radius:
        12px !important;

    padding:
        14px !important;

    margin:
        12px 0 !important;

    overflow-x: auto !important;
}


/* -----------------------------------------------------
   INLINE CODE
----------------------------------------------------- */

[data-testid="stChatMessage"] code {

    background:
        rgba(139, 92, 246, 0.14) !important;

    color:
        #DDD6FE !important;

    border-radius:
        6px !important;

    padding:
        2px 5px !important;
}


/* -----------------------------------------------------
   SOURCE EXPANDER
----------------------------------------------------- */

[data-testid="stChatMessage"]
[data-testid="stExpander"] {

    margin-top: 12px !important;

    border:
        1px solid rgba(167, 139, 250, 0.18) !important;

    border-radius:
        12px !important;

    background:
        rgba(139, 92, 246, 0.045) !important;

    overflow: hidden !important;
}


/* Source rows */

[data-testid="stChatMessage"]
[data-testid="stExpander"] p {

    font-size:
        0.84rem !important;

    line-height:
        1.5 !important;

    color:
        #C4B5FD !important;
}


/* -----------------------------------------------------
   MOBILE
----------------------------------------------------- */

@media (max-width: 768px) {

    [data-testid="stChatMessage"]:has(
        [data-testid="chatAvatarIcon-user"]
    ) {

        max-width: 88% !important;
    }


    [data-testid="stChatMessage"]:has(
        [data-testid="chatAvatarIcon-assistant"]
    ) {

        max-width: 96% !important;
    }
}
/* ============================================================
   NEXUS AI — CHAT UI POLISH
   ============================================================ */

/* Overall message spacing */
[data-testid="stChatMessage"] {
    margin-top: 10px !important;
    margin-bottom: 18px !important;
    padding: 16px 18px !important;
}

/* User message */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {
    max-width: 76% !important;
    padding: 14px 17px !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {
    max-width: 92% !important;
    padding: 17px 19px !important;
}

/* Improve paragraph readability */
[data-testid="stChatMessage"] p {
    font-size: 0.96rem !important;
    line-height: 1.7 !important;
}

/* Remove excessive spacing around the final paragraph */
[data-testid="stChatMessage"] p:last-child {
    margin-bottom: 0 !important;
}

/* Source expander inside assistant response */
[data-testid="stChatMessage"] [data-testid="stExpander"] {
    margin-top: 12px !important;
}

/* Code blocks inside answers */
[data-testid="stChatMessage"] pre {
    border-radius: 12px !important;
    margin-top: 10px !important;
    margin-bottom: 10px !important;
}

/* Inline code */
[data-testid="stChatMessage"] code {
    border-radius: 6px !important;
}

/* Keep assistant/user avatars compact */
[data-testid="stChatMessage"]
[data-testid^="chatAvatarIcon"] {
    min-width: 32px !important;
    min-height: 32px !important;
}
/* ============================================================
   NEXUS AI — PROFESSIONAL CHAT AVATARS
   ============================================================ */

[data-testid="stChatMessage"]
[data-testid^="chatAvatarIcon"] {
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    min-height: 34px !important;

    border-radius: 11px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    border: 1px solid rgba(167, 139, 250, 0.28) !important;

    box-shadow:
        0 5px 16px rgba(0, 0, 0, 0.18) !important;
}

/* NEXUS AI avatar */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
)
[data-testid^="chatAvatarIcon"] {
    background:
        linear-gradient(
            135deg,
            #8B5CF6,
            #6D28D9
        ) !important;
}

/* User avatar */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
)
[data-testid^="chatAvatarIcon"] {
    background:
        linear-gradient(
            135deg,
            #4C3A69,
            #302344
        ) !important;
}
/* ============================================================
   NEXUS AI — PREMIUM CHAT INPUT
   ============================================================ */

/* Main input container */
[data-testid="stChatInput"] {
    min-height: 56px !important;

    background:
        linear-gradient(
            135deg,
            rgba(139, 92, 246, 0.10),
            rgba(255, 255, 255, 0.035)
        ) !important;

    border: 1px solid
        rgba(167, 139, 250, 0.42) !important;

    border-radius: 28px !important;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.035) !important;

    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease !important;
}

/* Focus state */
[data-testid="stChatInput"]:focus-within {
    border-color:
        rgba(167, 139, 250, 0.78) !important;

    box-shadow:
        0 0 0 1px rgba(139, 92, 246, 0.28),
        0 12px 34px rgba(76, 29, 149, 0.20) !important;
}

/* Text area */
[data-testid="stChatInput"] textarea {
    min-height: 42px !important;

    padding-top: 10px !important;
    padding-bottom: 10px !important;

    font-size: 0.95rem !important;
    font-weight: 450 !important;

    line-height: 1.5 !important;
}

/* Placeholder */
[data-testid="stChatInput"]
textarea::placeholder {
    color:
        rgba(216, 208, 238, 0.62) !important;

    font-size: 0.93rem !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    min-height: 38px !important;

    margin-right: 7px !important;

    background:
        linear-gradient(
            135deg,
            #8B5CF6,
            #7C3AED
        ) !important;

    border:
        1px solid rgba(196, 181, 253, 0.45) !important;

    border-radius: 50% !important;

    box-shadow:
        0 5px 16px rgba(109, 40, 217, 0.30) !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease !important;
}

/* Send button hover */
[data-testid="stChatInput"] button:hover {
    transform: translateY(-1px) scale(1.04) !important;

    filter: brightness(1.08) !important;

    box-shadow:
        0 7px 20px rgba(109, 40, 217, 0.42) !important;
}

/* Send icon */
[data-testid="stChatInput"] button svg {
    width: 19px !important;
    height: 19px !important;

    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

/* Remove unwanted inner borders */
[data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* ============================================================
   NEXUS AI — SIDEBAR PREMIUM POLISH
   ============================================================ */

/* ------------------------------------------------------------
   SIDEBAR BRAND
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content h2 {
    letter-spacing: -0.02em !important;
    font-weight: 750 !important;

    background: linear-gradient(
        90deg,
        #F8F7FF,
        #C4B5FD
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.st-key-sidebar_scroll_content
[data-testid="stCaptionContainer"] {
    color: rgba(216, 208, 238, 0.62) !important;
}


/* ------------------------------------------------------------
   SIDEBAR DIVIDERS
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content hr {
    margin: 18px 0 !important;

    border-color:
        rgba(167, 139, 250, 0.12) !important;
}


/* ------------------------------------------------------------
   NEW CONVERSATION BUTTON
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content
.stButton > button {
    min-height: 43px !important;

    border-radius: 13px !important;

    font-weight: 600 !important;
    letter-spacing: 0.01em !important;

    border:
        1px solid rgba(196, 181, 253, 0.28) !important;

    box-shadow:
        0 7px 20px rgba(76, 29, 149, 0.16) !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease !important;
}

.st-key-sidebar_scroll_content
.stButton > button:hover {
    transform: translateY(-1px) !important;

    border-color:
        rgba(196, 181, 253, 0.52) !important;

    box-shadow:
        0 10px 26px rgba(76, 29, 149, 0.24) !important;
}


/* ------------------------------------------------------------
   KNOWLEDGE SOURCE UPLOAD CARD
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content
[data-testid="stFileUploader"] {
    border-radius: 16px !important;

    background:
        linear-gradient(
            145deg,
            rgba(139, 92, 246, 0.085),
            rgba(255, 255, 255, 0.025)
        ) !important;

    border:
        1px solid rgba(167, 139, 250, 0.18) !important;

    box-shadow:
        0 10px 26px rgba(0, 0, 0, 0.10) !important;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease !important;
}

.st-key-sidebar_scroll_content
[data-testid="stFileUploader"]:hover {
    border-color:
        rgba(167, 139, 250, 0.38) !important;

    box-shadow:
        0 12px 30px rgba(76, 29, 149, 0.14) !important;
}


/* ------------------------------------------------------------
   UPLOAD BUTTON
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content
[data-testid="stFileUploader"] button {
    border-radius: 10px !important;

    border:
        1px solid rgba(167, 139, 250, 0.28) !important;

    background:
        rgba(139, 92, 246, 0.08) !important;

    transition:
        background 0.18s ease,
        border-color 0.18s ease !important;
}

.st-key-sidebar_scroll_content
[data-testid="stFileUploader"] button:hover {
    background:
        rgba(139, 92, 246, 0.16) !important;

    border-color:
        rgba(167, 139, 250, 0.48) !important;
}


/* ------------------------------------------------------------
   ADD TO KNOWLEDGE BASE
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content
.stButton > button[kind="secondary"] {
    border-radius: 13px !important;
}


/* ------------------------------------------------------------
   SECTION TEXT
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content h3 {
    margin-bottom: 5px !important;

    font-weight: 680 !important;
    letter-spacing: -0.01em !important;
}


/* ------------------------------------------------------------
   CHAT MESSAGE COUNT
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content
[data-testid="stCaptionContainer"] p {
    font-size: 0.78rem !important;

    letter-spacing: 0.01em !important;
}


/* ------------------------------------------------------------
   SIDEBAR SCROLLBAR
   ------------------------------------------------------------ */

.st-key-sidebar_scroll_content::-webkit-scrollbar {
    width: 5px !important;
}

.st-key-sidebar_scroll_content::-webkit-scrollbar-track {
    background: transparent !important;
}

.st-key-sidebar_scroll_content::-webkit-scrollbar-thumb {
    background:
        rgba(167, 139, 250, 0.28) !important;

    border-radius: 10px !important;
}

.st-key-sidebar_scroll_content::-webkit-scrollbar-thumb:hover {
    background:
        rgba(167, 139, 250, 0.45) !important;
}
        </style>
        """,
        unsafe_allow_html=True,
    )