"""Presentation refinements using the established token variables."""

import streamlit as st


def apply_refinements() -> None:
    st.html(
        """
        <style>
        .bond-contextbar {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 8px 24px;
            padding: 10px 14px;
            margin-bottom: 28px;
            background: var(--bond-s-panel);
            border: 1px solid var(--bond-s-separator);
            border-radius: var(--bond-p-radius-control);
            color: var(--bond-s-foreground-secondary);
            font-size: var(--bond-p-text-small);
        }
        .bond-contextbar strong {
            color: var(--bond-s-accent);
            font-weight: 600;
        }
        .st-key-workspace_page [role="radiogroup"] {
            gap: 8px;
        }
        .st-key-workspace_page label {
            padding: 8px 10px;
            border: 1px solid transparent;
            border-radius: var(--bond-p-radius-control);
            min-height: 44px;
        }
        .st-key-workspace_page label:has(input:checked) {
            background: var(--bond-s-panel-raised);
            border-color: var(--bond-s-separator);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: var(--bond-p-radius-card);
        }
        [data-testid="stCaptionContainer"] {
            color: var(--bond-s-foreground-muted);
        }
        .bond-evidence-meta {
            color: var(--bond-s-foreground-secondary);
            font-size: var(--bond-p-text-small);
            margin: 8px 0 20px;
        }
        .bond-rule-title {
            color: var(--bond-s-foreground);
            margin: 0 0 8px;
        }
        @media (max-width: 640px) {
            .bond-contextbar {
                margin-bottom: 20px;
            }
        }
        </style>
        """
    )
