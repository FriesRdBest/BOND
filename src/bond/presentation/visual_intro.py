"""Cinematic full-screen introduction with background rays."""

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
            overflow: hidden;
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

        .bond-rays {
            position: absolute;
            inset: 0;
            opacity: 0;
            animation:
                bond-rays-in 600ms ease-out 500ms forwards,
                bond-rays-move 2750ms linear 500ms forwards;
        }

        .bond-rays::before,
        .bond-rays::after {
            content: "";
            position: absolute;
            top: -20%;
            bottom: -20%;
            width: 45%;
            background: linear-gradient(
                90deg,
                rgba(167, 139, 250, 0) 0%,
                rgba(167, 139, 250, 0.16) 45%,
                rgba(196, 181, 253, 0.10) 70%,
                rgba(167, 139, 250, 0) 100%
            );
            filter: blur(28px);
        }

        .bond-rays::before {
            left: -45%;
            animation: bond-ray-left 2750ms linear 500ms forwards;
        }

        .bond-rays::after {
            left: -20%;
            animation: bond-ray-right 2750ms linear 500ms forwards;
        }

        @keyframes bond-rays-in {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes bond-rays-move {
            from { transform: translateX(0); }
            to { transform: translateX(12%); }
        }

        @keyframes bond-ray-left {
            from { transform: translateX(0); }
            to { transform: translateX(320%); }
        }

        @keyframes bond-ray-right {
            from { transform: translateX(0); }
            to { transform: translateX(380%); }
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

        <div class="bond-intro">
            <div class="bond-rays"></div>
        </div>
        """
    )
