"""Typed assurance workflow values and controlled transition policy."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, StringConstraints, field_validator

from bond.domain.models import FrozenModel, Identifier, Label

Explanation = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
]


class WorkflowStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    VERIFIED = "verified"
    REVIEW_REQUIRED = "review_required"


class WorkflowEventKind(StrEnum):
    RECOMMENDATION_CREATED = "recommendation_created"
    APPROVAL_GRANTED = "approval_granted"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    SIMULATED_EXECUTION_RECORDED = "simulated_execution_recorded"
    VERIFICATION_PASSED = "verification_passed"
    VERIFICATION_FAILED = "verification_failed"


class WorkflowTransitionError(ValueError):
    """The requested workflow transition is not allowed."""


_ALLOWED_TRANSITIONS: dict[WorkflowStatus, tuple[WorkflowStatus, ...]] = {
    WorkflowStatus.PROPOSED: (
        WorkflowStatus.APPROVED,
        WorkflowStatus.REJECTED,
    ),
    WorkflowStatus.APPROVED: (WorkflowStatus.EXECUTED,),
    WorkflowStatus.EXECUTED: (
        WorkflowStatus.VERIFIED,
        WorkflowStatus.REVIEW_REQUIRED,
    ),
    WorkflowStatus.VERIFIED: (),
    WorkflowStatus.REVIEW_REQUIRED: (),
    WorkflowStatus.REJECTED: (),
}


def require_transition(current: WorkflowStatus, next_status: WorkflowStatus) -> None:
    if next_status not in _ALLOWED_TRANSITIONS[current]:
        raise WorkflowTransitionError(
            f"A recommendation in state {current.value} cannot move to {next_status.value}."
        )


class Recommendation(FrozenModel):
    id: UUID
    session_id: UUID
    service_id: Identifier
    rule_id: Identifier
    rule_version: str = "1"
    title: Label
    detail: Explanation
    owner: Label | None
    expected_result: Explanation
    status: WorkflowStatus = WorkflowStatus.PROPOSED
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("rule_version")
    @classmethod
    def validate_rule_version(cls, value: str) -> str:
        if not value or len(value) > 32:
            raise ValueError("Rule version must contain 1 to 32 characters.")
        return value


class WorkflowEvent(FrozenModel):
    id: UUID
    improvement_id: UUID
    session_id: UUID
    kind: WorkflowEventKind
    actor: Label
    detail: Explanation
    request_id: UUID
    occurred_at: AwareDatetime


class RecommendationDraft(FrozenModel):
    service_id: Identifier
    rule_id: Identifier
    rule_version: str = "1"
    title: Label
    detail: Explanation
    owner: Label | None = None
    expected_result: Explanation


class WorkflowDecision(FrozenModel):
    actor: Label
    reason: Explanation
    request_id: UUID


class ExecutionRecord(FrozenModel):
    actor: Label
    simulated_command: Label
    reason: Explanation
    request_id: UUID


class VerificationRecord(FrozenModel):
    actor: Label
    observed_result: Explanation
    passed: bool
    reason: Explanation
    request_id: UUID


def utc_now() -> datetime:
    return datetime.now(UTC)
