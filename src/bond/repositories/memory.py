"""Session isolated in memory workflow storage for the public demonstration."""

from collections.abc import Generator
from contextlib import contextmanager
from threading import RLock
from uuid import UUID

from bond.domain.workflow import Recommendation, WorkflowEvent


class InMemoryWorkflowRepository:
    """Ephemeral storage. It is not presented as durable production storage."""

    def __init__(self) -> None:
        self._recommendations: dict[UUID, Recommendation] = {}
        self._events: dict[UUID, list[WorkflowEvent]] = {}
        self._request_ids: set[UUID] = set()
        self._sessions: set[UUID] = set()
        self._transaction_lock = RLock()

    @contextmanager
    def atomic(self, session_id: UUID) -> Generator[None]:
        """Serialize participating operations and restore state on failure."""
        with self._transaction_lock:
            recommendations = self._recommendations.copy()
            events = {identifier: list(items) for identifier, items in self._events.items()}
            request_ids = self._request_ids.copy()
            sessions = self._sessions.copy()
            try:
                yield
            except BaseException:
                self._recommendations = recommendations
                self._events = events
                self._request_ids = request_ids
                self._sessions = sessions
                raise

    def ensure_session(self, session_id: UUID) -> None:
        self._sessions.add(session_id)

    def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        if recommendation.id in self._recommendations:
            raise ValueError("A recommendation with this identifier already exists.")
        self._recommendations[recommendation.id] = recommendation
        self._events[recommendation.id] = []
        return recommendation

    def get_recommendation(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> Recommendation | None:
        recommendation = self._recommendations.get(improvement_id)
        if recommendation is None or recommendation.session_id != session_id:
            return None
        return recommendation

    def list_recommendations(self, session_id: UUID) -> tuple[Recommendation, ...]:
        return tuple(
            recommendation
            for recommendation in self._recommendations.values()
            if recommendation.session_id == session_id
        )

    def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        current = self._recommendations.get(recommendation.id)
        if current is None or current.session_id != recommendation.session_id:
            raise ValueError("The recommendation does not exist in this session.")
        self._recommendations[recommendation.id] = recommendation
        return recommendation

    def append_event(self, event: WorkflowEvent) -> WorkflowEvent | None:
        if event.request_id in self._request_ids:
            return None
        recommendation = self._recommendations.get(event.improvement_id)
        if recommendation is None or recommendation.session_id != event.session_id:
            raise ValueError("The recommendation does not exist in this session.")
        self._request_ids.add(event.request_id)
        self._events[event.improvement_id].append(event)
        return event

    def find_event(
        self,
        improvement_id: UUID,
        session_id: UUID,
        request_id: UUID,
    ) -> WorkflowEvent | None:
        recommendation = self._recommendations.get(improvement_id)
        if recommendation is None or recommendation.session_id != session_id:
            return None

        for event in self._events.get(improvement_id, ()):
            if event.session_id == session_id and event.request_id == request_id:
                return event
        return None

    def list_events(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> tuple[WorkflowEvent, ...]:
        recommendation = self._recommendations.get(improvement_id)
        if recommendation is None or recommendation.session_id != session_id:
            return ()
        return tuple(self._events[improvement_id])
