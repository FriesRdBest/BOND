"""Controlled recommendation, approval, execution, and verification policy."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from bond.application_workflow import AssuranceWorkflow
from bond.domain.models import EvidenceSource, Service
from bond.domain.workflow import (
    ExecutionRecord,
    Recommendation,
    RecommendationDraft,
    VerificationRecord,
    WorkflowDecision,
    WorkflowStatus,
    WorkflowTransitionError,
)
from bond.repositories.memory import InMemoryWorkflowRepository

OBSERVED = datetime.now(UTC)


def service(**overrides: object) -> Service:
    values: dict[str, object] = {
        "id": "billing_export",
        "name": "Billing Export",
        "description": "Exports billing records.",
        "owner": "Finance Platform",
        "tier": 2,
        "contract_visible": False,
        "critical_vulnerabilities": 1,
        "observed_at": OBSERVED,
        "source": EvidenceSource.SYNTHETIC,
    }
    values.update(overrides)
    return Service.model_validate(values)


class StaticCatalog:
    def __init__(self, item: Service | None) -> None:
        self._item = item

    def list_services(self) -> tuple[Service, ...]:
        return () if self._item is None else (self._item,)

    def get_service(self, service_id: str) -> Service | None:
        if self._item is not None and self._item.id == service_id:
            return self._item
        return None


def workflow(item: Service | None = None) -> AssuranceWorkflow:
    return AssuranceWorkflow(
        StaticCatalog(item if item is not None else service()),
        InMemoryWorkflowRepository(),
    )


def draft() -> RecommendationDraft:
    return RecommendationDraft(
        service_id="billing_export",
        rule_id="contract_visible",
        title="Publish the billing export contract",
        detail="The contract evidence is not visible to reviewing teams.",
        expected_result="Contract evidence becomes visible in the catalog.",
    )


def test_proposal_requires_a_known_service() -> None:
    application = workflow(service(id="other_service"))
    with pytest.raises(ValueError, match="does not exist"):
        application.propose(uuid4(), draft(), uuid4())


def test_proposal_rejects_a_passing_rule() -> None:
    application = workflow(service(contract_visible=True))
    with pytest.raises(WorkflowTransitionError, match="passing rule"):
        application.propose(uuid4(), draft(), uuid4())


def test_proposal_uses_service_owner_by_default() -> None:
    application = workflow()
    recommendation = application.propose(uuid4(), draft(), uuid4())
    assert recommendation.owner == "Finance Platform"
    assert recommendation.status is WorkflowStatus.PROPOSED


def test_complete_workflow_records_distinct_events() -> None:
    application = workflow()
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())

    approved = application.approve(
        recommendation.id,
        session_id,
        WorkflowDecision(
            actor="Platform Owner",
            reason="The proposed contract publication is appropriate.",
            request_id=uuid4(),
        ),
    )
    assert approved is not None
    assert approved.status is WorkflowStatus.APPROVED

    executed = application.execute(
        recommendation.id,
        session_id,
        ExecutionRecord(
            actor="Automation",
            simulated_command="publish_contract_documentation",
            reason="The approved action is simulated in this demonstration.",
            request_id=uuid4(),
        ),
    )
    assert executed is not None
    assert executed.status is WorkflowStatus.EXECUTED

    verified = application.verify(
        recommendation.id,
        session_id,
        VerificationRecord(
            actor="Reviewer",
            observed_result="The contract evidence is now visible.",
            passed=True,
            reason="The expected result was observed.",
            request_id=uuid4(),
        ),
    )
    assert verified is not None
    assert verified.status is WorkflowStatus.VERIFIED

    events = application.history(recommendation.id, session_id)
    assert [event.kind for event in events] == [
        "recommendation_created",
        "approval_granted",
        "simulated_execution_recorded",
        "verification_passed",
    ]


def test_execution_requires_approval() -> None:
    application = workflow()
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())

    with pytest.raises(WorkflowTransitionError, match="cannot move"):
        application.execute(
            recommendation.id,
            session_id,
            ExecutionRecord(
                actor="Automation",
                simulated_command="publish_contract_documentation",
                reason="Attempted before approval.",
                request_id=uuid4(),
            ),
        )


def test_duplicate_request_does_not_duplicate_an_event() -> None:
    application = workflow()
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())
    request_id = uuid4()

    first = application.approve(
        recommendation.id,
        session_id,
        WorkflowDecision(
            actor="Platform Owner",
            reason="Approved once.",
            request_id=request_id,
        ),
    )
    repeated = application.approve(
        recommendation.id,
        session_id,
        WorkflowDecision(
            actor="Platform Owner",
            reason="Repeated request.",
            request_id=request_id,
        ),
    )

    assert first is not None
    assert repeated is not None
    assert repeated == first
    assert len(application.history(recommendation.id, session_id)) == 2


def test_recommendations_are_isolated_by_session() -> None:
    application = workflow()
    first_session = uuid4()
    second_session = uuid4()
    recommendation = application.propose(first_session, draft(), uuid4())

    assert application.recommendation(recommendation.id, second_session) is None
    assert application.recommendations(second_session) == ()
    assert application.history(recommendation.id, second_session) == ()
    with pytest.raises(ValueError, match="does not exist in this session"):
        application._recommendation(recommendation.id, second_session)


def test_invalid_draft_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RecommendationDraft(
            service_id="Invalid Service",
            rule_id="contract_visible",
            title="Publish contract",
            detail="The contract evidence is missing.",
            expected_result="The contract becomes visible.",
        )


def test_proposal_rejects_mismatched_rule_version() -> None:
    application = workflow()
    session_id = uuid4()
    stale_draft = draft().model_copy(update={"rule_version": "stale_version"})

    with pytest.raises(WorkflowTransitionError, match="rule version"):
        application.propose(session_id, stale_draft, uuid4())

    assert application.recommendations(session_id) == ()


def test_transition_request_cannot_be_reused_for_another_operation() -> None:
    application = workflow()
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())
    request_id = uuid4()
    decision = WorkflowDecision(
        actor="Platform Owner",
        reason="Approve the proposed improvement.",
        request_id=request_id,
    )

    approved = application.approve(recommendation.id, session_id, decision)
    assert approved is not None
    assert approved.status is WorkflowStatus.APPROVED

    with pytest.raises(WorkflowTransitionError, match="different operation"):
        application.reject(recommendation.id, session_id, decision)

    assert application.recommendation(recommendation.id, session_id) == approved
    assert len(application.history(recommendation.id, session_id)) == 2


def test_creation_request_cannot_be_reused_for_approval() -> None:
    application = workflow()
    session_id = uuid4()
    request_id = uuid4()
    recommendation = application.propose(session_id, draft(), request_id)

    with pytest.raises(WorkflowTransitionError, match="different operation"):
        application.approve(
            recommendation.id,
            session_id,
            WorkflowDecision(
                actor="Platform Owner",
                reason="Attempt to reuse the creation request.",
                request_id=request_id,
            ),
        )

    assert application.recommendation(recommendation.id, session_id) == recommendation
    assert len(application.history(recommendation.id, session_id)) == 1


def test_memory_transaction_rolls_back_failed_creation() -> None:
    repository = InMemoryWorkflowRepository()
    application = AssuranceWorkflow(StaticCatalog(service()), repository)
    session_id = uuid4()
    request_id = uuid4()

    with pytest.raises(RuntimeError, match="Injected creation failure"):
        with repository.atomic(session_id):
            application.propose(session_id, draft(), request_id)
            raise RuntimeError("Injected creation failure")

    assert application.recommendations(session_id) == ()

    with repository.atomic(session_id):
        retried = application.propose(session_id, draft(), request_id)

    assert len(application.recommendations(session_id)) == 1
    assert len(application.history(retried.id, session_id)) == 1


def test_memory_transaction_rolls_back_failed_transition() -> None:
    repository = InMemoryWorkflowRepository()
    application = AssuranceWorkflow(StaticCatalog(service()), repository)
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())
    decision = WorkflowDecision(
        actor="Platform Owner",
        reason="Verify rollback and retry.",
        request_id=uuid4(),
    )

    with pytest.raises(RuntimeError, match="Injected transition failure"):
        with repository.atomic(session_id):
            application.approve(recommendation.id, session_id, decision)
            raise RuntimeError("Injected transition failure")

    assert application.recommendation(recommendation.id, session_id) == recommendation
    assert len(application.history(recommendation.id, session_id)) == 1

    with repository.atomic(session_id):
        approved = application.approve(recommendation.id, session_id, decision)

    assert approved is not None
    assert approved.status is WorkflowStatus.APPROVED
    assert len(application.history(recommendation.id, session_id)) == 2


def test_memory_transaction_restores_state_after_nested_failure() -> None:
    repository = InMemoryWorkflowRepository()
    application = AssuranceWorkflow(StaticCatalog(service()), repository)
    session_id = uuid4()

    with repository.atomic(session_id):
        retained = application.propose(session_id, draft(), uuid4())
        with pytest.raises(RuntimeError, match="Injected nested failure"):
            with repository.atomic(session_id):
                application.propose(session_id, draft(), uuid4())
                raise RuntimeError("Injected nested failure")

        assert application.recommendations(session_id) == (retained,)

    assert application.recommendations(session_id) == (retained,)


def test_transition_rechecks_state_inside_transaction() -> None:
    class CompetingRepository(InMemoryWorkflowRepository):
        def get_recommendation(
            self,
            improvement_id: UUID,
            session_id: UUID,
        ) -> Recommendation | None:
            recommendation = super().get_recommendation(improvement_id, session_id)
            if recommendation is not None and self._reads >= 1:
                rejected = recommendation.model_copy(
                    update={
                        "status": WorkflowStatus.REJECTED,
                        "updated_at": recommendation.updated_at,
                    }
                )
                self.update_recommendation(rejected)
                return rejected
            self._reads += 1
            return recommendation

        def __init__(self) -> None:
            super().__init__()
            self._reads = 0

    repository = CompetingRepository()
    application = AssuranceWorkflow(StaticCatalog(service()), repository)
    session_id = uuid4()
    recommendation = application.propose(session_id, draft(), uuid4())
    repository._reads = 0

    with pytest.raises(WorkflowTransitionError, match="cannot move"):
        application.approve(
            recommendation.id,
            session_id,
            WorkflowDecision(
                actor="Platform Owner",
                reason="Attempted approval after a competing rejection.",
                request_id=uuid4(),
            ),
        )

    current = application.recommendation(recommendation.id, session_id)
    assert current is not None
    assert current.status is WorkflowStatus.REJECTED
    assert len(application.history(recommendation.id, session_id)) == 1
