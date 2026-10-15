"""Reviewer entry links select only recognized workspace pages."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize(
    ("view", "title"),
    [
        ("scorecard", "Scorecard Console"),
        ("catalog", "Catalog Repository"),
        ("pipeline", "Pipeline Laboratory"),
        ("engineering", "Engineering Notes"),
        ("unsupported", "Scorecard Console"),
    ],
)
def test_reviewer_entry_link(view: str, title: str) -> None:
    application = AppTest.from_file(str(APP), default_timeout=30)
    application.query_params["view"] = view
    application.run()
    assert not application.exception
    assert application.title[0].value == title
