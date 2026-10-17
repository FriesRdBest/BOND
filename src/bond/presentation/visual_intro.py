"""Cinematic full-screen introduction shell."""

import streamlit as st


def apply_intro_shell() -> None:
    st.html(
        """
        <style>
        .bond-intro {
            position: fixed;
            inset: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                radial-gradient(
                    ellipse at center,
                    rgba(0, 0, 0, 0) 0%,
                    rgba(0, 0, 0, 0.55) 55%,
                    rgba(0, 0, 0, 0.95) 100%
                ),
                #000;
            pointer-events: none;
            animation: bond-intro-out 500ms ease-in 4000ms forwards;
        }

        @keyframes bond-intro-out {
            to {
                opacity: 0;
                visibility: hidden;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .bond-intro {
                display: none !important;
            }
        }
        </style>

        <div class="bond-intro"></div>
        """
    )
