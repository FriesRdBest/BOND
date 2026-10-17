"""Non-blocking loading introduction for the visual upgrade."""

import streamlit as st


def apply_loading_experience() -> None:
    st.html(
        """
        <style>
        .bond-loader {
            position: fixed;
            inset: 0;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bond-p-canvas);
            pointer-events: none;
            animation: bond-loader-out 800ms ease-in 700ms forwards;
        }

        .bond-loader-inner {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }

        .bond-loader-mark {
            width: 54px;
            height: 54px;
            display: grid;
            place-items: center;
            border-radius: 16px;
            color: #111216;
            font-size: 22px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--bond-p-violet), var(--bond-p-lavender));
            animation: bond-loader-pulse 1.1s ease-in-out infinite;
        }

        .bond-loader-bar {
            width: 180px;
            height: 4px;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.08);
        }

        .bond-loader-bar::after {
            content: "";
            display: block;
            width: 45%;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--bond-p-violet), var(--bond-p-lavender));
            animation: bond-loader-slide 1s ease-in-out infinite;
        }

        @keyframes bond-loader-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.06); }
        }

        @keyframes bond-loader-slide {
            from { transform: translateX(-100%); }
            to { transform: translateX(240%); }
        }

        @keyframes bond-loader-out {
            to { opacity: 0; visibility: hidden; }
        }

        @media (prefers-reduced-motion: reduce) {
            .bond-loader { display: none !important; }
        }
        </style>

        <div class="bond-loader">
            <div class="bond-loader-inner">
                <div class="bond-loader-mark">◈</div>
                <div class="bond-loader-bar"></div>
            </div>
        </div>
        """
    )
