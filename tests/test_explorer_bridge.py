"""Bridge validation helpers and native fallback checks."""

from bond.presentation.explorer import _selection_value, assets_available


def test_component_assets_are_available() -> None:
    assert assets_available()


def test_dictionary_result_is_read_without_execution() -> None:
    message = {"service_id": "billing_export"}
    assert _selection_value({"selection": message}, "selection") == message


def test_missing_result_value_is_empty() -> None:
    assert _selection_value({}, "selection") is None


def test_attribute_result_is_supported() -> None:
    class Result:
        selection = "example"

    assert _selection_value(Result(), "selection") == "example"
