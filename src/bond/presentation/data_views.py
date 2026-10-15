"""Typed boundary for the collection inputs used by BOND.

Streamlit's broad data annotation contains unresolved external types.
Explicit callable assumptions are isolated here and supported by
forwarding, signature, and application execution tests.
"""

from collections.abc import Mapping, Sequence
from typing import Literal, Protocol, cast

import streamlit as st

Cell = str | int | float | bool | None


class _TableRenderer(Protocol):
    def __call__(
        self,
        data: Sequence[Mapping[str, Cell]],
        *,
        hide_index: bool,
        width: Literal["stretch"],
    ) -> object: ...


class _LineRenderer(Protocol):
    def __call__(
        self,
        data: Mapping[str, Sequence[float]],
        *,
        color: str,
        height: int,
    ) -> object: ...


def _resolve_renderer(name: str) -> object:
    renderer: object = getattr(st, name)
    if not callable(renderer):
        raise TypeError("The requested Streamlit renderer is not callable.")
    return renderer


def render_table(
    data: Sequence[Mapping[str, Cell]],
    *,
    hide_index: bool = True,
    width: Literal["stretch"] = "stretch",
) -> None:
    renderer = cast(_TableRenderer, _resolve_renderer("dataframe"))
    renderer(data, hide_index=hide_index, width=width)


def render_line_chart(
    data: Mapping[str, Sequence[float]],
    *,
    color: str,
    height: int,
) -> None:
    renderer = cast(_LineRenderer, _resolve_renderer("line_chart"))
    renderer(data, color=color, height=height)
