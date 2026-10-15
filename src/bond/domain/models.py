"""Validated immutable values for the initial catalog."""

from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints

Identifier = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9_]{2,63}$"),
]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class FrozenModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )


class EvidenceSource(StrEnum):
    SYNTHETIC = "synthetic"
    INTEGRATION = "integration"


class RuleStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class Service(FrozenModel):
    id: Identifier
    name: Label
    description: Label
    owner: Label | None
    tier: int = Field(ge=1, le=3)
    dependencies: tuple[Identifier, ...] = ()
    contract_visible: bool | None
    critical_vulnerabilities: int | None = Field(default=None, ge=0)
    observed_at: AwareDatetime
    source: EvidenceSource = EvidenceSource.SYNTHETIC


class RuleResult(FrozenModel):
    rule_id: Identifier
    version: str = "1"
    status: RuleStatus
    explanation: Label


class ScoreSummary(FrozenModel):
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    unknown: int = Field(ge=0)
    total: int = Field(ge=0)

    @property
    def score_percent(self) -> float | None:
        if self.total == 0:
            return None
        return round(self.passed / self.total * 100, 1)

    @property
    def evidence_coverage_percent(self) -> float | None:
        if self.total == 0:
            return None
        return round((self.passed + self.failed) / self.total * 100, 1)
