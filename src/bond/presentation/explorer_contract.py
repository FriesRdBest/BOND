"""Validated component contracts. Browser messages are untrusted."""

from collections.abc import Collection
from typing import Literal, Self
from uuid import UUID

from pydantic import Field, ValidationError, model_validator

from bond.application import OrganizationSnapshot, ServiceAssessment
from bond.domain.models import FrozenModel, Identifier
from bond.presentation.styles import DesignTokens, load_tokens


class ExplorerPayload(FrozenModel):
    schema_version: Literal[1] = 1
    selected_service_id: Identifier | None = None
    services: tuple[ServiceAssessment, ...] = Field(max_length=200)
    tokens: DesignTokens

    @model_validator(mode="after")
    def validate_selection_and_identity(self) -> Self:
        identifiers = {assessment.service.id for assessment in self.services}
        if len(identifiers) != len(self.services):
            raise ValueError("Explorer services must have unique identifiers.")
        if self.selected_service_id is not None and self.selected_service_id not in identifiers:
            raise ValueError("The initial selection must reference a supplied service.")
        return self


class SelectionMessage(FrozenModel):
    schema_version: Literal[1]
    action: Literal["inspect_service"]
    service_id: Identifier
    request_id: UUID


def build_explorer_payload(
    snapshot: OrganizationSnapshot,
    selected_service_id: str | None = None,
) -> ExplorerPayload:
    return ExplorerPayload(
        selected_service_id=selected_service_id,
        services=snapshot.assessments,
        tokens=load_tokens(),
    )


def validate_selection(
    value: object,
    allowed_service_ids: Collection[str],
) -> SelectionMessage | None:
    try:
        message = SelectionMessage.model_validate(value)
    except ValidationError:
        return None
    if message.service_id not in allowed_service_ids:
        return None
    return message
