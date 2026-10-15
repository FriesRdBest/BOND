"""Transient inspection requests are captured, validated, and consumed once."""

import pytest

from bond.presentation import explorer

REQUEST = {
    "schema_version": 1,
    "action": "inspect_service",
    "service_id": "billing_export",
    "request_id": "00000000-0000-4000-8000-000000000001",
}


def test_callback_captures_a_valid_inspection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {
        explorer.COMPONENT_KEY: {"selection": dict(REQUEST)},
        "_bond_explorer_allowed_ids": ("billing_export",),
    }
    monkeypatch.setattr(explorer.st, "session_state", state)

    explorer._selection_changed()
    message, rejected = explorer._consume_selection(None, {"billing_export"})

    assert message is not None
    assert message.service_id == "billing_export"
    assert state[explorer.NATIVE_SELECTION_KEY] == "billing_export"
    assert not rejected
    assert "_bond_explorer_pending_selection" not in state


def test_callback_rejects_a_service_outside_the_view(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {
        explorer.COMPONENT_KEY: {"selection": dict(REQUEST)},
        "_bond_explorer_allowed_ids": ("identity_gateway",),
    }
    monkeypatch.setattr(explorer.st, "session_state", state)

    explorer._selection_changed()
    message, rejected = explorer._consume_selection(None, {"identity_gateway"})

    assert message is None
    assert rejected


def test_current_view_is_checked_again_when_consuming(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {
        explorer.COMPONENT_KEY: {"selection": dict(REQUEST)},
        "_bond_explorer_allowed_ids": ("billing_export",),
    }
    monkeypatch.setattr(explorer.st, "session_state", state)

    explorer._selection_changed()
    message, rejected = explorer._consume_selection(None, {"identity_gateway"})

    assert message is None
    assert rejected


def test_duplicate_request_is_not_consumed_twice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {}
    monkeypatch.setattr(explorer.st, "session_state", state)

    first, rejected = explorer._consume_selection(
        {"selection": dict(REQUEST)},
        {"billing_export"},
    )
    second, second_rejected = explorer._consume_selection(
        {"selection": dict(REQUEST)},
        {"billing_export"},
    )

    assert first is not None
    assert not rejected
    assert second is None
    assert not second_rejected


def test_empty_callback_does_not_invent_an_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {
        explorer.COMPONENT_KEY: {"selection": None},
        "_bond_explorer_allowed_ids": ("billing_export",),
    }
    monkeypatch.setattr(explorer.st, "session_state", state)

    explorer._selection_changed()
    message, rejected = explorer._consume_selection(None, {"billing_export"})

    assert message is None
    assert not rejected
