"""Framework independent repository contracts."""

from contextlib import AbstractContextManager
from typing import Protocol
from uuid import UUID

from bond.domain.models import Service
from bond.domain.workflow import Recommendation, WorkflowEvent


class CatalogRepository(Protocol):
    def list_services(self) -> tuple[Service, ...]: ...

    def get_service(self, service_id: str) -> Service | None: ...


class WorkflowRepository(Protocol):
    def atomic(self, session_id: UUID) -> AbstractContextManager[None]:
        """Run participating writes in one recoverable transaction."""
        ...

    def ensure_session(self, session_id: UUID) -> None: ...

    def create_recommendation(self, recommendation: Recommendation) -> Recommendation: ...

    def get_recommendation(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> Recommendation | None: ...

    def list_recommendations(self, session_id: UUID) -> tuple[Recommendation, ...]: ...

    def update_recommendation(self, recommendation: Recommendation) -> Recommendation: ...

    def append_event(self, event: WorkflowEvent) -> WorkflowEvent | None: ...

    def find_event(
        self,
        improvement_id: UUID,
        session_id: UUID,
        request_id: UUID,
    ) -> WorkflowEvent | None: ...

    def list_events(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> tuple[WorkflowEvent, ...]: ...
