"""Console interaction checks without a visual browser review."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_catalog_native_view_remains_available() -> None:
    application = AppTest.from_file(str(APP), default_timeout=30).run()
    application.sidebar.radio[0].set_value("Catalog Repository").run()
    assert not application.exception

    toggle = next(
        element for element in application.toggle if element.label == "Use native evidence view"
    )
    toggle.set_value(True).run()
    assert not application.exception
    assert any(element.label == "Inspect service" for element in application.selectbox)


def test_catalog_status_filter_has_an_empty_state() -> None:
    application = AppTest.from_file(str(APP), default_timeout=30).run()
    application.sidebar.radio[0].set_value("Catalog Repository").run()
    application.text_input[0].set_value("Identity Gateway").run()

    result_filter = next(
        element for element in application.selectbox if element.label == "Rule results"
    )
    result_filter.set_value("Needs attention").run()
    assert not application.exception
    assert any("No services match" in element.value for element in application.info)


def test_scorecard_can_open_an_affected_service() -> None:
    application = AppTest.from_file(str(APP), default_timeout=30).run()
    button = next(
        element for element in application.button if element.key == "attention_billing_export"
    )
    button.click().run()
    assert not application.exception
    assert application.title[0].value == "Catalog Repository"
    selected = next(
        element for element in application.selectbox if element.label == "Inspect service"
    )
    assert selected.value == "billing_export"
