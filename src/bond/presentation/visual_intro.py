"""Cinematic full-screen introduction with rays, slot title, and exit."""

import streamlit as st


def apply_intro_shell() -> None:
    st.html(
        """
        <style>
        .bond-intro {
            position: fixed;
            inset: 0;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #000;
            pointer-events: auto;
            animation: bond-intro-out 500ms ease-in 4000ms forwards;
        }

        .bond-rays {
            position: absolute;
            inset: 0;
        }

        .bond-line {
            position: absolute;
            left: -30%;
            width: 30%;
            height: 2px;
            background: linear-gradient(
                90deg,
                rgba(207, 194, 254, 0) 0%,
                #CFC2FE 50%,
                rgba(207, 194, 254, 0) 100%
            );
            filter: blur(0.4px);
            opacity: 0;
            animation: bond-line-pass 2750ms linear 500ms infinite;
        }

        .bond-line:nth-child(1) { top: 18%; animation-delay: 500ms; }
        .bond-line:nth-child(2) { top: 32%; animation-delay: 850ms; }
        .bond-line:nth-child(3) { top: 47%; animation-delay: 620ms; }
        .bond-line:nth-child(4) { top: 61%; animation-delay: 980ms; }
        .bond-line:nth-child(5) { top: 74%; animation-delay: 720ms; }
        .bond-line:nth-child(6) { top: 86%; animation-delay: 1100ms; }

        .bond-title {
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.06em;
            font-size: min(9.5vw, 19vh);
            font-weight: 900;
            letter-spacing: 0.02em;
            color: #FFFFFF;
            text-shadow: 0 0 34px rgba(207, 194, 254, 0.35);
            animation:
                bond-title-blink 2750ms steps(1, end) 500ms forwards,
                bond-title-solid 200ms ease-out 3250ms forwards;
        }

        .bond-slot {
            display: inline-block;
            min-width: 0.58em;
            text-align: center;
        }

        @keyframes bond-title-blink {
            0%, 12% { opacity: 0.15; }
            18%, 30% { opacity: 1; }
            36%, 48% { opacity: 0.25; }
            54%, 66% { opacity: 1; }
            72%, 84% { opacity: 0.35; }
            90%, 100% { opacity: 1; }
        }

        @keyframes bond-title-solid {
            from { opacity: 1; }
            to { opacity: 1; }
        }

        @keyframes bond-line-pass {
            0% {
                transform: translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 0.9;
            }
            90% {
                opacity: 0.9;
            }
            100% {
                transform: translateX(440%);
                opacity: 0;
            }
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
            <div class="bond-rays">
                <div class="bond-line"></div>
                <div class="bond-line"></div>
                <div class="bond-line"></div>
                <div class="bond-line"></div>
                <div class="bond-line"></div>
                <div class="bond-line"></div>
            </div>
            <div class="bond-title" id="bond-title">- b-o-n-d -</div>
        </div>

        <script>
        (function () {
            const target = "- b-o-n-d -";
            const container = document.getElementById("bond-title");
            if (!container) return;
            const chars = Array.from(target);
            container.textContent = "";
            const spans = chars.map((character) => {
                const span = document.createElement("span");
                span.className = "bond-slot";
                span.textContent = character === " " ? "\u00a0" : "A";
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
                        span.textContent = character === " " ? "\u00a0" : character;
                    });
                    return;
                }
                spans.forEach((span, index) => {
                    const character = chars[index];
                    if (character === " " || character === "-") {
                        span.textContent = character === " " ? "\u00a0" : character;
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
