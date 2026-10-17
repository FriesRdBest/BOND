"""Motion and interaction layer for the visual upgrade."""

import streamlit as st


def apply_motion() -> None:
    st.html(
        """
        <style>
        .stApp {
            animation: bond-app-enter 420ms cubic-bezier(0.22, 1, 0.36, 1) both;
        }

        @keyframes bond-app-enter {
            from {
                opacity: 0;
                transform: translateY(10px) scale(0.995);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        [data-testid="stMetric"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            animation: bond-rise 520ms cubic-bezier(0.22, 1, 0.36, 1) both;
        }

        @keyframes bond-rise {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .stApp button,
        .stApp a,
        .stApp input,
        .stApp select,
        .stApp textarea {
            transition:
                border-color 170ms ease-out,
                background-color 170ms ease-out,
                box-shadow 170ms ease-out,
                transform 170ms ease-out;
        }

        .stApp button:focus-visible,
        .stApp a:focus-visible,
        .stApp input:focus-visible,
        .stApp select:focus-visible,
        .stApp textarea:focus-visible {
            outline: 2px solid var(--bond-c-control-focus) !important;
            outline-offset: 2px;
        }

        @media (prefers-reduced-motion: reduce) {
            .stApp,
            [data-testid="stMetric"],
            [data-testid="stVerticalBlockBorderWrapper"] {
                animation: none !important;
                transition: none !important;
                transform: none !important;
            }
        }
        </style>
        """
    )
