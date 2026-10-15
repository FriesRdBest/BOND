"""Assurance API for synthetic evidence and controlled workflow demonstrations."""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from bond.application import CatalogApplication, OrganizationSnapshot, ServiceAssessment
from bond.demo import WarehouseWindow, warehouse_fixture
from bond.domain.workflow import (
    ExecutionRecord,
    Recommendation,
    RecommendationDraft,
    VerificationRecord,
    WorkflowDecision,
    WorkflowEvent,
)
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.workflow_runtime import MEMORY_MODE, build_workflow_runtime

app = FastAPI(
    title="BOND assurance API",
    version="0.2.0",
    description=(
        "Independent portfolio demonstration. Synthetic evidence, controlled "
        "recommendations, simulated execution, and no production actions."
    ),
)

catalog_application = CatalogApplication(FixtureCatalogRepository())
workflow_runtime = build_workflow_runtime(MEMORY_MODE)


class SessionRequest(BaseModel):
    session_id: UUID


class RecommendationRequest(BaseModel):
    session_id: UUID
    request_id: UUID
    service_id: str
    rule_id: str
    rule_version: str = "1"
    title: str = Field(min_length=1, max_length=160)
    detail: str = Field(min_length=1, max_length=1000)
    owner: str | None = Field(default=None, max_length=160)
    expected_result: str = Field(min_length=1, max_length=1000)


class DecisionRequest(BaseModel):
    session_id: UUID
    request_id: UUID
    actor: str = Field(min_length=1, max_length=160)
    reason: str = Field(min_length=1, max_length=1000)


class ExecutionRequest(BaseModel):
    session_id: UUID
    request_id: UUID
    actor: str = Field(min_length=1, max_length=160)
    simulated_command: str = Field(min_length=1, max_length=160)
    reason: str = Field(min_length=1, max_length=1000)


class VerificationRequest(BaseModel):
    session_id: UUID
    request_id: UUID
    actor: str = Field(min_length=1, max_length=160)
    observed_result: str = Field(min_length=1, max_length=1000)
    passed: bool
    reason: str = Field(min_length=1, max_length=1000)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "synthetic",
        "workflow_store": workflow_runtime.mode,
    }


@app.get("/api/v1/scorecard", response_model=OrganizationSnapshot)
def scorecard() -> OrganizationSnapshot:
    return catalog_application.snapshot()


@app.get("/api/v1/catalog", response_model=list[ServiceAssessment])
def catalog(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServiceAssessment]:
    return list(catalog_application.snapshot().assessments[offset : offset + limit])


@app.get("/api/v1/catalog/{service_id}", response_model=ServiceAssessment)
def service_detail(service_id: str) -> ServiceAssessment:
    assessment = catalog_application.assess(service_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    return assessment


@app.get("/api/v1/telemetry", response_model=WarehouseWindow)
def telemetry() -> WarehouseWindow:
    return warehouse_fixture()


@app.post("/api/v1/workflow/sessions", status_code=204)
def open_session(request: SessionRequest) -> None:
    workflow_runtime.open_session(request.session_id)


@app.get(
    "/api/v1/workflow/sessions/{session_id}/recommendations",
    response_model=list[Recommendation],
)
def recommendations(session_id: UUID) -> list[Recommendation]:
    return list(workflow_runtime.application.recommendations(session_id))


@app.post("/api/v1/workflow/recommendations", response_model=Recommendation)
def create_recommendation(request: RecommendationRequest) -> Recommendation:
    workflow_runtime.open_session(request.session_id)
    try:
        return workflow_runtime.application.propose(
            request.session_id,
            RecommendationDraft(
                service_id=request.service_id,
                rule_id=request.rule_id,
                rule_version=request.rule_version,
                title=request.title,
                detail=request.detail,
                owner=request.owner,
                expected_result=request.expected_result,
            ),
            request.request_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get(
    "/api/v1/workflow/recommendations/{improvement_id}",
    response_model=Recommendation,
)
def recommendation(
    improvement_id: UUID,
    session_id: Annotated[UUID, Query()],
) -> Recommendation:
    item = workflow_runtime.application.recommendation(improvement_id, session_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return item


@app.post(
    "/api/v1/workflow/recommendations/{improvement_id}/approval",
    response_model=Recommendation,
)
def approve_recommendation(
    improvement_id: UUID,
    request: DecisionRequest,
) -> Recommendation:
    return _decision(
        improvement_id,
        request,
        workflow_runtime.application.approve,
    )


@app.post(
    "/api/v1/workflow/recommendations/{improvement_id}/rejection",
    response_model=Recommendation,
)
def reject_recommendation(
    improvement_id: UUID,
    request: DecisionRequest,
) -> Recommendation:
    return _decision(
        improvement_id,
        request,
        workflow_runtime.application.reject,
    )


@app.post(
    "/api/v1/workflow/recommendations/{improvement_id}/execution",
    response_model=Recommendation,
)
def execute_recommendation(
    improvement_id: UUID,
    request: ExecutionRequest,
) -> Recommendation:
    workflow_runtime.open_session(request.session_id)
    try:
        result = workflow_runtime.application.execute(
            improvement_id,
            request.session_id,
            ExecutionRecord(
                actor=request.actor,
                simulated_command=request.simulated_command,
                reason=request.reason,
                request_id=request.request_id,
            ),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if result is None:
        return _existing(improvement_id, request.session_id)
    return result


@app.post(
    "/api/v1/workflow/recommendations/{improvement_id}/verification",
    response_model=Recommendation,
)
def verify_recommendation(
    improvement_id: UUID,
    request: VerificationRequest,
) -> Recommendation:
    workflow_runtime.open_session(request.session_id)
    try:
        result = workflow_runtime.application.verify(
            improvement_id,
            request.session_id,
            VerificationRecord(
                actor=request.actor,
                observed_result=request.observed_result,
                passed=request.passed,
                reason=request.reason,
                request_id=request.request_id,
            ),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if result is None:
        return _existing(improvement_id, request.session_id)
    return result


@app.get(
    "/api/v1/workflow/recommendations/{improvement_id}/events",
    response_model=list[WorkflowEvent],
)
def events(
    improvement_id: UUID,
    session_id: Annotated[UUID, Query()],
) -> list[WorkflowEvent]:
    return list(workflow_runtime.application.history(improvement_id, session_id))


def _decision(
    improvement_id: UUID,
    request: DecisionRequest,
    action: Callable[
        [UUID, UUID, WorkflowDecision],
        Recommendation | None,
    ],
) -> Recommendation:
    workflow_runtime.open_session(request.session_id)
    try:
        result = action(
            improvement_id,
            request.session_id,
            WorkflowDecision(
                actor=request.actor,
                reason=request.reason,
                request_id=request.request_id,
            ),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if result is None:
        return _existing(improvement_id, request.session_id)
    return result


def _existing(improvement_id: UUID, session_id: UUID) -> Recommendation:
    item = workflow_runtime.application.recommendation(improvement_id, session_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return item
