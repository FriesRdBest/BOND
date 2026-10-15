"""Verify the supported presentation boundary without suppressing diagnostics."""

import inspect
from collections.abc import Mapping, Sequence
from typing import Literal

import pytest
import streamlit as st

from bond.presentation.data_views import Cell, render_line_chart, render_table


def test_table_adapter_forwards_supported_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, bool, str]] = []

    def capture(
        data: Sequence[Mapping[str, Cell]],
        *,
        hide_index: bool,
        width: Literal["stretch"],
    ) -> object:
        calls.append((data, hide_index, width))
        return object()

    monkeypatch.setattr(st, "dataframe", capture)
    rows: list[dict[str, Cell]] = [{"Service": "Example", "Score": 75}]
    render_table(rows)
    assert calls == [(rows, True, "stretch")]


def test_chart_adapter_forwards_supported_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, str, int]] = []

    def capture(
        data: Mapping[str, Sequence[float]],
        *,
        color: str,
        height: int,
    ) -> object:
        calls.append((data, color, height))
        return object()

    monkeypatch.setattr(st, "line_chart", capture)
    samples = {"Latency": [100.0, 200.0]}
    render_line_chart(samples, color="#A78BFA", height=260)
    assert calls == [(samples, "#A78BFA", 260)]


@pytest.mark.parametrize(
    ("attribute", "required"),
    [
        ("dataframe", {"data", "hide_index", "width"}),
        ("line_chart", {"data", "color", "height"}),
    ],
)
def test_installed_streamlit_exposes_required_parameters(
    attribute: str,
    required: set[str],
) -> None:
    parameters = inspect.signature(getattr(st, attribute)).parameters
    assert required.issubset(parameters)
