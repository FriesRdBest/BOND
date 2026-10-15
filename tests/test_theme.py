"""Ensure native theme values remain aligned with the token source."""

import tomllib
from pathlib import Path

from bond.presentation.styles import load_tokens


def test_streamlit_theme_matches_tokens() -> None:
    root = Path(__file__).resolve().parents[1]
    configuration = tomllib.loads((root / ".streamlit/config.toml").read_text(encoding="utf-8"))
    primitives = load_tokens().primitives
    theme = configuration["theme"]
    assert theme["backgroundColor"] == primitives["canvas"]
    assert theme["secondaryBackgroundColor"] == primitives["surface"]
    assert theme["primaryColor"] == primitives["violet"]
    assert theme["textColor"] == primitives["text"]
