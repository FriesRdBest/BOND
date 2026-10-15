"""Component messages cannot select services outside the supplied view."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from bond.application import CatalogApplication
from bond.presentation.explorer_contract import (
    ExplorerPayload,
    build_explorer_payload,
    validate_selection,
)
from bond.repositories.fixtures import FixtureCatalogRepository


def valid_message() -> dict[str, object]:
    return {
        "schema_version": 1,
        "action": "inspect_service",
        "service_id": "billing_export",
        "request_id": "00000000-0000-4000-8000-000000000001",
    }


def test_payload_uses_the_shared_snapshot() -> None:
    snapshot = CatalogApplication(FixtureCatalogRepository()).snapshot()
    payload = build_explorer_payload(snapshot, "billing_export")
    assert len(payload.services) == 6
    assert payload.selected_service_id == "billing_export"
    assert payload.tokens.primitives["canvas"] == "#111216"


def test_valid_known_service_message_is_accepted() -> None:
    message = validate_selection(valid_message(), {"billing_export"})
    assert message is not None
    assert message.request_id == UUID("00000000-0000-4000-8000-000000000001")


def test_unknown_service_message_is_rejected() -> None:
    assert validate_selection(valid_message(), {"identity_gateway"}) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", 99),
        ("action", "execute_production_change"),
        ("service_id", "../../private"),
        ("request_id", "not_a_uuid"),
    ],
)
def test_invalid_message_fields_are_rejected(field: str, value: object) -> None:
    message = valid_message()
    message[field] = value
    assert validate_selection(message, {"billing_export"}) is None


def test_extra_message_fields_are_rejected() -> None:
    message = valid_message()
    message["administrative_override"] = True
    assert validate_selection(message, {"billing_export"}) is None


def test_unknown_initial_selection_is_rejected() -> None:
    snapshot = CatalogApplication(FixtureCatalogRepository()).snapshot()
    payload = build_explorer_payload(snapshot).model_dump()
    payload["selected_service_id"] = "not_present"
    with pytest.raises(ValidationError):
        ExplorerPayload.model_validate(payload)


def test_duplicate_service_identity_is_rejected() -> None:
    snapshot = CatalogApplication(FixtureCatalogRepository()).snapshot()
    payload = build_explorer_payload(snapshot).model_dump()
    payload["services"] = [payload["services"][0], payload["services"][0]]
    with pytest.raises(ValidationError):
        ExplorerPayload.model_validate(payload)
