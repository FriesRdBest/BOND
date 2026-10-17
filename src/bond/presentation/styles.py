"""Resolve the three token tiers into scoped application styles."""

from importlib.resources import files

import streamlit as st
from pydantic import BaseModel, ConfigDict


class DesignTokens(BaseModel):
    model_config = ConfigDict(extra="forbid")
    primitives: dict[str, str]
    semantic: dict[str, str]
    components: dict[str, str]


def load_tokens() -> DesignTokens:
    tokens = DesignTokens.model_validate_json(
        files("bond.data").joinpath("design_tokens.json").read_text(encoding="utf-8")
    )
    if any(reference not in tokens.primitives for reference in tokens.semantic.values()):
        raise ValueError("A semantic token references an unknown primitive.")
    if any(reference not in tokens.semantic for reference in tokens.components.values()):
        raise ValueError("A component token references an unknown semantic role.")
    return tokens


def apply_styles() -> None:
    tokens = load_tokens()
    declarations = [
        f"--bond-p-{name.replace('_', '-')}: {value};" for name, value in tokens.primitives.items()
    ]
    declarations.extend(
        f"--bond-s-{name.replace('_', '-')}: var(--bond-p-{reference.replace('_', '-')});"
        for name, reference in tokens.semantic.items()
    )
    declarations.extend(
        f"--bond-c-{name.replace('_', '-')}: var(--bond-s-{reference.replace('_', '-')});"
        for name, reference in tokens.components.items()
    )
    variables = "\n".join(declarations)

    st.html(
        "<style>:root {"
        + variables
        + "}"
        + """
        .stApp {
            background: var(--bond-c-page-background);
            color: var(--bond-s-foreground);
            font-family: var(--bond-p-font-body);
            font-size: var(--bond-p-text-body);
            line-height: 1.5;
        }
        .block-container {
            max-width: 1480px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 {
            letter-spacing: -0.025em;
            line-height: 1.2;
        }
        h1 { font-size: var(--bond-p-text-page) !important; }
        h2 { font-size: var(--bond-p-text-section) !important; }
        [data-testid="stSidebar"] {
            background: var(--bond-s-panel);
            border-right: 1px solid var(--bond-s-separator);
        }
        [data-testid="stMetric"] {
            background: var(--bond-c-card-background);
            border: 1px solid var(--bond-s-separator);
            border-radius: var(--bond-p-radius-card);
            padding: var(--bond-p-space-card);
            font-variant-numeric: tabular-nums;
        }
        [data-testid="stMetricValue"] {
            font-size: var(--bond-p-text-metric);
            letter-spacing: -0.035em;
        }
        .bond-eyebrow {
            color: var(--bond-s-accent);
            font-size: var(--bond-p-text-small);
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }
        .bond-introduction {
            max-width: 780px;
            color: var(--bond-s-foreground-secondary);
            font-size: var(--bond-p-text-explanation);
            margin-bottom: var(--bond-p-space-section);
        }
        .bond-status {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border: 1px solid currentColor;
            border-radius: var(--bond-p-radius-control);
            font-size: var(--bond-p-text-small);
            margin-bottom: 0.5rem;
        }
        .bond-pass { color: var(--bond-c-status-pass); }
        .bond-fail { color: var(--bond-c-status-fail); }
        .bond-unknown { color: var(--bond-c-status-warning); }
        button, a, input, select, textarea {
            transition:
                border-color var(--bond-p-motion-control) ease-out,
                background-color var(--bond-p-motion-control) ease-out;
        }
        button:focus-visible, a:focus-visible, input:focus-visible,
        select:focus-visible, textarea:focus-visible {
            outline: var(--bond-p-focus-width) solid var(--bond-c-control-focus) !important;
            outline-offset: 2px;
        }
        code, pre {
            font-family: var(--bond-p-font-mono);
        }
        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.5rem;
            }
        }
        @media (prefers-reduced-motion: reduce) {
            .stApp *, .stApp *::before, .stApp *::after {
                animation: none !important;
                transition: none !important;
                scroll-behavior: auto !important;
            }
        }
        </style>
        """
    )
