"""Validated callback capture for transient Streamlit inspection events."""

from collections.abc import Callable, Mapping, Sequence
from importlib.resources import files
from typing import Protocol, cast

import streamlit as st
import streamlit.components.v2 as components

from bond.application import OrganizationSnapshot
from bond.presentation.explorer_contract import (
    SelectionMessage,
    build_explorer_payload,
    validate_selection,
)

COMPONENT_KEY = "catalog_evidence_explorer"
NATIVE_SELECTION_KEY = "catalog_selected_service"
_ALLOWED_KEY = "_bond_explorer_allowed_ids"
_PENDING_KEY = "_bond_explorer_pending_selection"
_REJECTED_KEY = "_bond_explorer_rejected_selection"
_LAST_REQUEST_KEY = "_bond_explorer_last_request"


class _ComponentRenderer(Protocol):
    def __call__(
        self,
        *,
        data: object,
        key: str,
        default: dict[str, object],
        on_selection_change: Callable[[], None],
    ) -> object: ...


def _selection_value(result: object, name: str) -> object:
    if isinstance(result, Mapping):
        return cast(Mapping[str, object], result).get(name)
    return getattr(result, name, None)


def _allowed_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    return tuple(
        identifier for identifier in cast(Sequence[object], value) if isinstance(identifier, str)
    )


def _selection_changed() -> None:
    """Capture and validate the transient value before the main render."""
    component_state: object = st.session_state.get(COMPONENT_KEY)
    value = _selection_value(component_state, "selection")

    if value is None:
        return

    allowed_state: object = st.session_state.get(_ALLOWED_KEY)
    message = validate_selection(value, _allowed_ids(allowed_state))

    if message is None:
        st.session_state.pop(_PENDING_KEY, None)
        st.session_state[_REJECTED_KEY] = True
        return

    st.session_state[_PENDING_KEY] = message.model_dump(mode="json")
    st.session_state[NATIVE_SELECTION_KEY] = message.service_id


def _consume_selection(
    result: object,
    allowed: set[str],
) -> tuple[SelectionMessage | None, bool]:
    rejected = st.session_state.pop(_REJECTED_KEY, False) is True
    value: object = st.session_state.pop(_PENDING_KEY, None)

    if value is None:
        value = _selection_value(result, "selection")
    if value is None:
        return None, rejected

    message = validate_selection(value, allowed)
    if message is None:
        return None, True

    request_id = str(message.request_id)
    if st.session_state.get(_LAST_REQUEST_KEY) == request_id:
        return None, rejected

    st.session_state[_LAST_REQUEST_KEY] = request_id
    return message, rejected


def assets_available() -> bool:
    directory = files("bond.data").joinpath("web", "evidence")
    return all(
        directory.joinpath(name).is_file()
        for name in ("evidence.js", "evidence.css", "build_manifest.json")
    )


@st.cache_resource(show_spinner=False)
def _registered_component() -> _ComponentRenderer:
    renderer = components.component(
        "bond.evidence_explorer",
        html='<div id="bond-evidence-root"></div>',
        css="evidence.css",
        js="evidence.js",
        isolate_styles=True,
    )
    return cast(_ComponentRenderer, renderer)


def render_explorer(
    snapshot: OrganizationSnapshot,
    selected_service_id: str | None,
) -> SelectionMessage | None:
    if not assets_available():
        st.info("The visual explorer is unavailable. Native evidence inspection remains below.")
        return None

    allowed = {assessment.service.id for assessment in snapshot.assessments}
    st.session_state[_ALLOWED_KEY] = tuple(sorted(allowed))

    pending, rejected = _consume_selection(None, allowed)
    effective_selection = pending.service_id if pending is not None else selected_service_id

    payload = build_explorer_payload(snapshot, effective_selection)

    result = _registered_component()(
        data=payload.model_dump(mode="json"),
        key=COMPONENT_KEY,
        default={"selection": None},
        on_selection_change=_selection_changed,
    )

    if pending is not None:
        message = pending
    else:
        message, result_rejected = _consume_selection(result, allowed)
        rejected = rejected or result_rejected

    if rejected:
        st.warning("An invalid inspection request was ignored. No action was performed.")

    return message
