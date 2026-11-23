"""
theme.py - Google Antigravity Design System & Theme Engine for Streamlit.
Provides design tokens, custom CSS injection, and chart styling matching https://antigravity.google/.
"""

import streamlit as st

# Google Antigravity Design Tokens
TOKENS = {
    "bg": "#FFFFFF",
    "bg_alt": "#F8F9FC",
    "surface": "#FFFFFF",
    "surface_card": "rgba(255, 255, 255, 0.92)",
    "border": "#E3E7EF",
    "border_subtle": "#EEF2F6",
    "text_primary": "#1F1F1F",
    "text_muted": "#5F6368",
    "primary": "#1A73E8",
    "primary_hover": "#1557B0",
    "primary_tint": "#E8F0FE",
    "gradient_start": "#4285F4",
    "gradient_mid": "#A142F4",
    "gradient_end": "#F538A0",
    "success": "#34A853",
    "success_tint": "#E6F4EA",
    "warning": "#FBBC04",
    "warning_tint": "#FEF7E0",
    "error": "#EA4335",
    "error_tint": "#FCE8E6",
    "radius_card": "16px",
    "radius_pill": "999px",
    "radius_input": "10px",
    "shadow_card": "0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.03)",
    "shadow_hover": "0 6px 24px rgba(26, 115, 232, 0.12), 0 2px 6px rgba(0, 0, 0, 0.04)",
}


def apply_theme():
    """Injects the Google Antigravity visual theme stylesheet into Streamlit."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {
        --ag-bg: #FFFFFF;
        --ag-bg-alt: #F8F9FC;
        --ag-surface: #FFFFFF;
        --ag-surface-card: rgba(255, 255, 255, 0.92);
        --ag-border: #E3E7EF;
        --ag-border-subtle: #EEF2F6;
        --ag-text-primary: #1F1F1F;
        --ag-text-muted: #5F6368;
        --ag-primary: #1A73E8;
        --ag-primary-hover: #1557B0;
        --ag-primary-tint: #E8F0FE;
        --ag-gradient: linear-gradient(135deg, #4285F4 0%, #A142F4 52%, #F538A0 100%);
        --ag-gradient-subtle: linear-gradient(135deg, rgba(66, 133, 244, 0.08) 0%, rgba(161, 66, 244, 0.08) 50%, rgba(245, 56, 160, 0.08) 100%);
        --ag-radius-pill: 999px;
        --ag-radius-card: 16px;
        --ag-radius-input: 10px;
        --ag-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
        --ag-shadow-md: 0 4px 16px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02);
        --ag-shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.02);
        --ag-success: #34A853;
        --ag-warning: #FBBC04;
        --ag-error: #EA4335;
    }

    /* Core typography & page canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Google Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: transparent !important;
        color: var(--ag-text-primary) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Transparent containers allowing cursor canvas to render in background */
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stHeader"] {
        border-bottom: 1px solid rgba(227, 231, 239, 0.6) !important;
        backdrop-filter: blur(8px) !important;
    }

    [data-testid="stToolbar"] {
        background-color: transparent !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1360px !important;
        position: relative;
        z-index: 1;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Google Sans', 'Inter', sans-serif !important;
        color: var(--ag-text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }

    p, span, .stMarkdown, .stCaption {
        color: var(--ag-text-muted) !important;
        font-size: 0.94rem;
        line-height: 1.6;
    }

    strong, b {
        color: var(--ag-text-primary) !important;
    }

    label, [data-testid="stWidgetLabel"] p {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: var(--ag-text-primary) !important;
        letter-spacing: -0.01em !important;
    }

    /* Antigravity Gradient Text Utility */
    .ag-gradient-text {
        background: var(--ag-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        display: inline-block;
    }

    /* Sidebar - Clean light frosted surface */
    [data-testid="stSidebar"] {
        background-color: rgba(248, 249, 252, 0.88) !important;
        border-right: 1px solid var(--ag-border) !important;
        backdrop-filter: blur(14px) !important;
        position: relative;
        z-index: 2;
    }

    [data-testid="stSidebar"] * {
        color: var(--ag-text-primary);
    }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] p {
        color: var(--ag-text-muted) !important;
    }

    /* Pill-Shaped Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: var(--ag-radius-pill) !important;
        font-family: 'Google Sans', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        padding: 0 24px !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
        cursor: pointer !important;
    }

    /* Primary Filled Button (Google Blue) */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {
        background: var(--ag-primary) !important;
        color: #FFFFFF !important;
        border: 1px solid transparent !important;
        box-shadow: 0 1px 3px rgba(26, 115, 232, 0.25), 0 4px 12px rgba(26, 115, 232, 0.15) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {
        background: var(--ag-primary-hover) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(26, 115, 232, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary Outlined Button */
    .stButton > button:not([kind="primary"]) {
        background: rgba(255, 255, 255, 0.95) !important;
        color: var(--ag-text-primary) !important;
        border: 1px solid var(--ag-border) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--ag-primary) !important;
        color: var(--ag-primary) !important;
        background: var(--ag-primary-tint) !important;
        transform: translateY(-1px) !important;
    }

    /* Form Inputs, Selectboxes & Textareas */
    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--ag-text-primary) !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: var(--ag-radius-input) !important;
        font-size: 0.93rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--ag-primary) !important;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.18) !important;
        outline: none !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9AA0A6 !important;
    }

    /* Pill-Shaped Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(241, 243, 248, 0.85) !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: var(--ag-radius-pill) !important;
        padding: 5px !important;
        gap: 6px !important;
        backdrop-filter: blur(8px) !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--ag-text-muted) !important;
        font-family: 'Google Sans', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 20px !important;
        border-radius: var(--ag-radius-pill) !important;
        border: none !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--ag-primary) !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: var(--ag-primary) !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }

    /* Metric Cards - Antigravity Glass Cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.90) !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: var(--ag-radius-card) !important;
        padding: 18px 22px !important;
        box-shadow: var(--ag-shadow-md) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: var(--ag-shadow-lg) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stMetric"] label {
        color: var(--ag-text-muted) !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ag-text-primary) !important;
        font-family: 'Google Sans', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.85rem !important;
    }

    /* Streamlit Containers with border */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.90) !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: var(--ag-radius-card) !important;
        box-shadow: var(--ag-shadow-md) !important;
        backdrop-filter: blur(10px) !important;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.90) !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: 14px !important;
        box-shadow: var(--ag-shadow-sm) !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px) !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--ag-text-primary) !important;
        font-weight: 600 !important;
        padding: 14px 18px !important;
        border-radius: 14px !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: var(--ag-primary) !important;
        background-color: var(--ag-bg-alt) !important;
    }

    /* Alert Boxes */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid var(--ag-border) !important;
        font-size: 0.90rem !important;
    }

    /* Dataframe & Tables */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--ag-border) !important;
        border-radius: 14px !important;
        box-shadow: var(--ag-shadow-sm) !important;
        overflow: hidden !important;
    }

    /* Dividers */
    hr {
        border-color: var(--ag-border-subtle) !important;
        margin: 1.8rem 0 !important;
    }

    /* Clean Streamlit chrome adjustments */
    #MainMenu, footer {
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


def style_chart(fig):
    """
    Applies the clean Google Antigravity light theme styling to Plotly figures.
    """
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255, 255, 255, 0.92)",
        plot_bgcolor="rgba(255, 255, 255, 0.92)",
        font=dict(color="#1F1F1F", family="Google Sans, Inter, sans-serif"),
        title_font=dict(color="#1F1F1F", size=14, family="Google Sans, Inter, sans-serif"),
        legend=dict(font=dict(color="#5F6368")),
        margin=dict(l=20, r=20, t=40, b=20),
        colorway=["#1A73E8", "#A142F4", "#F538A0", "#34A853", "#FBBC04", "#4285F4", "#EA4335"],
    )
    fig.update_xaxes(
        gridcolor="#EEF2F6",
        linecolor="#E3E7EF",
        tickfont=dict(color="#5F6368"),
        title_font=dict(color="#5F6368")
    )
    fig.update_yaxes(
        gridcolor="#EEF2F6",
        linecolor="#E3E7EF",
        tickfont=dict(color="#5F6368"),
        title_font=dict(color="#5F6368")
    )
    return fig
