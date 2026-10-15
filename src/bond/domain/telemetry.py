"""Explicit metric semantics without external integration dependencies."""

import math
from collections.abc import Sequence
from decimal import Decimal


def p95_latency_ms(samples: Sequence[float]) -> float | None:
    """Use nearest rank on finite nonnegative latency samples."""
    if not samples:
        return None
    if any(not math.isfinite(value) or value < 0 for value in samples):
        raise ValueError("Latency samples must be finite and nonnegative.")
    ordered = sorted(samples)
    index = math.ceil(len(ordered) * 0.95) - 1
    return ordered[index]


def hourly_credit_burn(credits: Decimal, window_seconds: int) -> Decimal:
    """Return credits per hour, not currency."""
    if not credits.is_finite() or credits < 0:
        raise ValueError("Credits must be finite and nonnegative.")
    if window_seconds <= 0:
        raise ValueError("The observation window must be positive.")
    return credits * Decimal(3600) / Decimal(window_seconds)
