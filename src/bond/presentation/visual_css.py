"""Core CSS upgrade for surfaces, controls, and data views."""

import streamlit as st


def apply_core_css() -> None:
    st.html(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(167, 139, 250, 0.08), transparent 38%),
                radial-gradient(circle at 88% 92%, rgba(196, 181, 253, 0.06), transparent 42%),
                var(--bond-c-page-background);
        }

        h1 {
            background: linear-gradient(100deg, var(--bond-p-text), var(--bond-p-lavender));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(34, 37, 46, 0.96), var(--bond-p-surface));
            border-right: 1px solid var(--bond-s-separator);
            box-shadow: 12px 0 40px rgba(0, 0, 0, 0.16);
        }

        .st-key-workspace_page label {
            min-height: 46px;
            padding: 10px 12px;
            border: 1px solid transparent;
            border-radius: 12px;
            transition:
                background-color 170ms ease-out,
                border-color 170ms ease-out,
                transform 170ms ease-out;
        }

        .st-key-workspace_page label:hover {
            background: rgba(255, 255, 255, 0.045);
            border-color: rgba(167, 139, 250, 0.35);
            transform: translateX(3px);
        }

        .st-key-workspace_page label:has(input:checked) {
            background: linear-gradient(
                100deg,
                rgba(167, 139, 250, 0.16),
                rgba(196, 181, 253, 0.08)
            );
            border-color: rgba(167, 139, 250, 0.55);
            box-shadow: inset 3px 0 0 var(--bond-p-violet);
        }

        .bond-contextbar {
            backdrop-filter: blur(10px);
            background: rgba(26, 28, 35, 0.82);
            border: 1px solid rgba(167, 139, 250, 0.22);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
        }

        [data-testid="stMetric"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--bond-s-separator);
            border-radius: var(--bond-p-radius-card);
            background:
                linear-gradient(160deg, rgba(255, 255, 255, 0.035), transparent 55%),
                var(--bond-c-card-background);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.13);
            transition:
                border-color 180ms ease-out,
                box-shadow 180ms ease-out,
                transform 180ms ease-out;
        }

        [data-testid="stMetric"]:hover,
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(167, 139, 250, 0.48);
            box-shadow: 0 16px 40px rgba(167, 139, 250, 0.15);
            transform: translateY(-3px);
        }

        [data-testid="stMetric"]::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--bond-p-violet), transparent);
            opacity: 0.65;
        }

        .stApp button[kind="primary"] {
            border: none;
            color: #111216;
            font-weight: 700;
            background: linear-gradient(135deg, var(--bond-p-violet), var(--bond-p-lavender));
            box-shadow: 0 10px 26px rgba(167, 139, 250, 0.22);
        }

        .stApp button[kind="primary"]:hover {
            filter: brightness(1.07);
            transform: translateY(-1px);
        }

        .stApp button[kind="secondary"] {
            border: 1px solid var(--bond-s-separator);
            background: rgba(255, 255, 255, 0.035);
        }

        .stApp button[kind="secondary"]:hover {
            border-color: rgba(167, 139, 250, 0.45);
            background: rgba(167, 139, 250, 0.10);
        }

        .stApp input,
        .stApp select,
        .stApp textarea {
            border: 1px solid var(--bond-s-separator);
            border-radius: 10px;
        }

        .stApp input:focus,
        .stApp select:focus,
        .stApp textarea:focus {
            border-color: var(--bond-p-lavender);
            box-shadow: 0 0 0 3px rgba(196, 181, 253, 0.16);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--bond-s-separator);
            border-radius: var(--bond-p-radius-card);
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
        }

        [data-testid="stArrowVegaLiteChart"] {
            border: 1px solid var(--bond-s-separator);
            border-radius: var(--bond-p-radius-card);
            padding: 12px;
            background: rgba(255, 255, 255, 0.025);
        }

        .bond-status {
            backdrop-filter: blur(6px);
            border-radius: 999px;
            padding: 0.28rem 0.75rem;
            font-weight: 600;
        }

        .bond-pass {
            border-color: rgba(16, 185, 129, 0.45);
            background: rgba(16, 185, 129, 0.10);
        }

        .bond-fail {
            border-color: rgba(248, 113, 113, 0.45);
            background: rgba(248, 113, 113, 0.10);
        }

        .bond-unknown {
            border-color: rgba(245, 158, 11, 0.45);
            background: rgba(245, 158, 11, 0.10);
        }

        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-thumb {
            border-radius: 999px;
            background: rgba(167, 139, 250, 0.35);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(167, 139, 250, 0.55);
        }
        </style>
        """
    )
