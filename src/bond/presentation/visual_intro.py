"""Cinematic full-screen introduction with rays, slot title, and exit."""

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

        .bond-title {
            position: relative;
            z-index: 2;
            display: flex;
            gap: 0.18em;
            font-size: clamp(3rem, 12vw, 9rem);
            font-weight: 800;
            letter-spacing: 0.08em;
            color: #F4F3F8;
            text-shadow: 0 0 34px rgba(167, 139, 250, 0.35);
        }

        .bond-slot {
            display: inline-block;
            min-width: 0.62em;
            text-align: center;
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
            <div class="bond-title" id="bond-title"></div>
        </div>

        <script>
        (function () {
            const target = "- b-o-n-d -";
            const container = document.getElementById("bond-title");
            if (!container) return;
            const chars = Array.from(target);
            const spans = chars.map((character) => {
                const span = document.createElement("span");
                span.className = "bond-slot";
                span.textContent = character === " " ? "\u00A0" : "A";
                container.appendChild(span);
                return span;
            });
            const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            const start = performance.now() + 500;
            const rollDuration = 2750;
            function tick(now) {
                const elapsed = now - start;
                if (elapsed < 0) {
                    requestAnimationFrame(tick);
                    return;
                }
                if (elapsed >= rollDuration) {
                    spans.forEach((span, index) => {
                        const character = chars[index];
                        span.textContent = character === " " ? "\u00A0" : character;
                    });
                    return;
                }
                spans.forEach((span, index) => {
                    const character = chars[index];
                    if (character === " " || character === "-") {
                        span.textContent = character === " " ? "\u00A0" : character;
                        return;
                    }
                    span.textContent = alphabet[Math.floor(Math.random() * alphabet.length)];
                });
                requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
        })();
        </script>
        """
    )
