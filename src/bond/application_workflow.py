"""Evidence to verification workflow policy, independent of interfaces."""

from uuid import UUID, uuid4

from bond.domain.models import RuleStatus, Service
from bond.domain.rules import evaluate_service
from bond.domain.workflow import (
    ExecutionRecord,
    Recommendation,
    RecommendationDraft,
    VerificationRecord,
    WorkflowDecision,
    WorkflowEvent,
    WorkflowEventKind,
    WorkflowStatus,
    WorkflowTransitionError,
    require_transition,
    utc_now,
)
from bond.repositories.interfaces import CatalogRepository, WorkflowRepository


class AssuranceWorkflow:
    """Controls recommendation state changes and records their history."""

    def __init__(
        self,
        catalog: CatalogRepository,
        workflows: WorkflowRepository,
    ) -> None:
        self._catalog = catalog
        self._workflows = workflows

    def _service(self, service_id: str) -> Service:
        service = self._catalog.get_service(service_id)
        if service is None:
            raise ValueError("The selected service does not exist.")
        return service

    def _recommendation(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> Recommendation:
        recommendation = self._workflows.get_recommendation(
            improvement_id,
            session_id,
        )
        if recommendation is None:
            raise ValueError("The recommendation does not exist in this session.")
        return recommendation

    def recommendation(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> Recommendation | None:
        return self._workflows.get_recommendation(improvement_id, session_id)

    def _transition(
        self,
        recommendation: Recommendation,
        next_status: WorkflowStatus,
        event_kind: WorkflowEventKind,
        actor: str,
        detail: str,
        request_id: UUID,
    ) -> Recommendation | None:
        with self._workflows.atomic(recommendation.session_id):
            existing = self._workflows.find_event(
                recommendation.id,
                recommendation.session_id,
                request_id,
            )
            if existing is not None:
                if existing.kind != event_kind:
                    raise WorkflowTransitionError(
                        "The request identifier was already used for a different operation."
                    )
                return recommendation

            require_transition(recommendation.status, next_status)

            event = WorkflowEvent(
                id=uuid4(),
                improvement_id=recommendation.id,
                session_id=recommendation.session_id,
                kind=event_kind,
                actor=actor,
                detail=detail,
                request_id=request_id,
                occurred_at=utc_now(),
            )

            recorded = self._workflows.append_event(event)
            if recorded is None:
                return None

            updated = recommendation.model_copy(
                update={
                    "status": next_status,
                    "updated_at": event.occurred_at,
                }
            )
            return self._workflows.update_recommendation(updated)

    def open_session(self, session_id: UUID) -> None:
        self._workflows.ensure_session(session_id)

    def propose(
        self,
        session_id: UUID,
        draft: RecommendationDraft,
        request_id: UUID,
    ) -> Recommendation:
        self._workflows.ensure_session(session_id)
        service = self._service(draft.service_id)
        results = evaluate_service(service)

        matching = next(
            (result for result in results if result.rule_id == draft.rule_id),
            None,
        )

        if matching is None:
            raise ValueError("The selected rule does not apply to this service.")

        if draft.rule_version != matching.version:
            raise WorkflowTransitionError(
                "The submitted rule version does not match the evaluated evidence."
            )

        if matching.status == RuleStatus.PASS:
            raise WorkflowTransitionError(
                "A passing rule result cannot create an improvement recommendation."
            )

        timestamp = utc_now()
        recommendation = Recommendation(
            id=uuid4(),
            session_id=session_id,
            service_id=service.id,
            rule_id=draft.rule_id,
            rule_version=draft.rule_version,
            title=draft.title,
            detail=draft.detail,
            owner=draft.owner or service.owner,
            expected_result=draft.expected_result,
            status=WorkflowStatus.PROPOSED,
            created_at=timestamp,
            updated_at=timestamp,
        )

        event = WorkflowEvent(
            id=uuid4(),
            improvement_id=recommendation.id,
            session_id=session_id,
            kind=WorkflowEventKind.RECOMMENDATION_CREATED,
            actor="BOND",
            detail=(
                f"Recommendation created from {draft.rule_id} version "
                f"{draft.rule_version} evidence."
            ),
            request_id=request_id,
            occurred_at=timestamp,
        )
        with self._workflows.atomic(session_id):
            created = self._workflows.create_recommendation(recommendation)
            self._workflows.append_event(event)
        return created

    def approve(
        self,
        improvement_id: UUID,
        session_id: UUID,
        decision: WorkflowDecision,
    ) -> Recommendation | None:
        recommendation = self._recommendation(improvement_id, session_id)
        return self._transition(
            recommendation,
            WorkflowStatus.APPROVED,
            WorkflowEventKind.APPROVAL_GRANTED,
            decision.actor,
            decision.reason,
            decision.request_id,
        )

    def reject(
        self,
        improvement_id: UUID,
        session_id: UUID,
        decision: WorkflowDecision,
    ) -> Recommendation | None:
        recommendation = self._recommendation(improvement_id, session_id)
        return self._transition(
            recommendation,
            WorkflowStatus.REJECTED,
            WorkflowEventKind.RECOMMENDATION_REJECTED,
            decision.actor,
            decision.reason,
            decision.request_id,
        )

    def execute(
        self,
        improvement_id: UUID,
        session_id: UUID,
        execution: ExecutionRecord,
    ) -> Recommendation | None:
        recommendation = self._recommendation(improvement_id, session_id)
        return self._transition(
            recommendation,
            WorkflowStatus.EXECUTED,
            WorkflowEventKind.SIMULATED_EXECUTION_RECORDED,
            execution.actor,
            (f"Simulated command recorded: {execution.simulated_command}. {execution.reason}"),
            execution.request_id,
        )

    def verify(
        self,
        improvement_id: UUID,
        session_id: UUID,
        verification: VerificationRecord,
    ) -> Recommendation | None:
        recommendation = self._recommendation(improvement_id, session_id)
        next_status = (
            WorkflowStatus.VERIFIED if verification.passed else WorkflowStatus.REVIEW_REQUIRED
        )
        event_kind = (
            WorkflowEventKind.VERIFICATION_PASSED
            if verification.passed
            else WorkflowEventKind.VERIFICATION_FAILED
        )
        return self._transition(
            recommendation,
            next_status,
            event_kind,
            verification.actor,
            (f"Verification observed: {verification.observed_result}. {verification.reason}"),
            verification.request_id,
        )

    def history(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> tuple[WorkflowEvent, ...]:
        if self.recommendation(improvement_id, session_id) is None:
            return ()
        return self._workflows.list_events(improvement_id, session_id)

    def recommendations(self, session_id: UUID) -> tuple[Recommendation, ...]:
        return self._workflows.list_recommendations(session_id)
