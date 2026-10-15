"""Explicitly synthetic warehouse window shared by the UI and API."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field

from bond.domain.models import FrozenModel
from bond.domain.telemetry import hourly_credit_burn, p95_latency_ms

Latency = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class WarehouseWindow(FrozenModel):
    warehouse: str
    source: Literal["synthetic"] = "synthetic"
    observed_at: AwareDatetime
    window_seconds: int = Field(gt=0)
    credits_consumed: Decimal = Field(ge=0)
    latencies_ms: tuple[Latency, ...]

    @property
    def p95_ms(self) -> float | None:
        return p95_latency_ms(self.latencies_ms)

    @property
    def credits_per_hour(self) -> Decimal:
        return hourly_credit_burn(self.credits_consumed, self.window_seconds)


def warehouse_fixture() -> WarehouseWindow:
    return WarehouseWindow.model_validate(
        {
            "warehouse": "ANALYTICS_REVIEW",
            "source": "synthetic",
            "observed_at": "2026-10-15T12:00:00Z",
            "window_seconds": 3600,
            "credits_consumed": "2.40",
            "latencies_ms": [120, 145, 132, 280, 410, 165, 190, 870, 220, 155],
        }
    )
