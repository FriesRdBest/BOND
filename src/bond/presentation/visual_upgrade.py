"""Optional visual refinements: entrance animation and palette polish."""

import streamlit as st


def apply_visual_upgrade() -> None:
    st.html(
        """
        <style>
        .stApp { animation: bond-app-enter 360ms ease-out both; }
        @keyframes bond-app-enter {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stApp [data-testid="stMetric"],
        .stApp [data-testid="stVerticalBlockBorderWrapper"] {
            animation: bond-card-enter 420ms ease-out both;
        }
        @keyframes bond-card-enter {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stApp [data-testid="stMetric"] {
            transition: border-color 160ms ease-out, box-shadow 160ms ease-out, transform 160ms ease-out;
        }
        .stApp [data-testid="stMetric"]:hover {
            border-color: var(--bond-s-accent);
            box-shadow: 0 8px 24px rgba(167, 139, 250, 0.16);
            transform: translateY(-2px);
        }
        .stApp button[kind="primary"] {
            background: linear-gradient(135deg, var(--bond-p-violet), var(--bond-p-lavender));
            border: none; color: #111216; font-weight: 600;
        }
        .stApp button[kind="primary"]:hover { filter: brightness(1.06); }
        [data-testid="stSidebar"] [data-testid="stRadio"] { gap: 0.15rem; }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
            transition: background-color 160ms ease-out, color 160ms ease-out, transform 160ms ease-out;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
            background: rgba(167, 139, 250, 0.10); transform: translateX(3px);
        }
        /* Keep the native radio inputs and accessible labels intact. */
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"]::before {
            content: var(--bond-nav-marker);
            display: inline-block; flex: 0 0 2.4em;
            margin-right: 0.65rem; text-align: center;
            white-space: pre; color: var(--bond-s-accent);
            font-size: 0.875rem; font-weight: 600;
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"]:nth-of-type(1) {
            --bond-nav-marker: "- b -"; --bond-nav-name: "Scorecard Console";
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"]:nth-of-type(2) {
            --bond-nav-marker: "- o -"; --bond-nav-name: "Catalog Repository";
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"]:nth-of-type(3) {
            --bond-nav-marker: "- n -"; --bond-nav-name: "Pipeline Laboratory";
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"]:nth-of-type(4) {
            --bond-nav-marker: "- d -"; --bond-nav-name: "Engineering Notes";
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label [data-testid="stMarkdownContainer"] p {
            color: var(--bond-s-accent); font-weight: 600; letter-spacing: 0.02em;
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
            font-size: 0; letter-spacing: 0;
        }
        [data-testid="stSidebar"] .st-key-workspace_page label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p::after {
            content: var(--bond-nav-name); font-size: 0.875rem; letter-spacing: 0.02em;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] {
            pointer-events: none;
        }
        @media (prefers-reduced-motion: reduce) {
            .stApp, .stApp [data-testid="stMetric"],
            .stApp [data-testid="stVerticalBlockBorderWrapper"],
            [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
                animation: none !important; transition: none !important; transform: none !important;
            }
        }
        </style>
        """
    )
