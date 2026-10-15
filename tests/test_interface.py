"""Automated Streamlit execution checks, not a visual accessibility audit."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize(
    "page",
    [
        "Scorecard Console",
        "Catalog Repository",
        "Pipeline Laboratory",
        "Engineering Notes",
    ],
)
def test_workspace_pages_execute(page: str) -> None:
    application = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not application.exception
    application.sidebar.radio[0].set_value(page).run()
    assert not application.exception
    assert application.title[0].value == page


def test_catalog_search_empty_state() -> None:
    application = AppTest.from_file(str(APP), default_timeout=30).run()
    application.sidebar.radio[0].set_value("Catalog Repository").run()
    application.text_input[0].set_value("no_matching_service_123").run()
    assert not application.exception
    assert any("No services match" in item.value for item in application.info)
