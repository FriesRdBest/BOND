"""Durable PostgreSQL workflow adapter with session scoped reads and writes."""

from uuid import UUID

from bond.config import DatabaseSettings
from bond.domain.workflow import Recommendation, WorkflowEvent
from bond.infrastructure.database import connect_database

_RECOMMENDATION_COLUMNS = """
    id,
    session_id,
    service_id,
    rule_id,
    rule_version,
    title,
    detail,
    owner,
    expected_result,
    status,
    created_at,
    updated_at
"""

_EVENT_COLUMNS = """
    id,
    improvement_id,
    session_id,
    kind,
    actor,
    detail,
    request_id,
    occurred_at
"""


def _recommendation(row: tuple[object, ...]) -> Recommendation:
    return Recommendation.model_validate(
        {
            "id": row[0],
            "session_id": row[1],
            "service_id": row[2],
            "rule_id": row[3],
            "rule_version": row[4],
            "title": row[5],
            "detail": row[6],
            "owner": row[7],
            "expected_result": row[8],
            "status": row[9],
            "created_at": row[10],
            "updated_at": row[11],
        }
    )


def _event(row: tuple[object, ...]) -> WorkflowEvent:
    return WorkflowEvent.model_validate(
        {
            "id": row[0],
            "improvement_id": row[1],
            "session_id": row[2],
            "kind": row[3],
            "actor": row[4],
            "detail": row[5],
            "request_id": row[6],
            "occurred_at": row[7],
        }
    )


class PostgresWorkflowRepository:
    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings

    def ensure_session(self, session_id: UUID) -> None:
        with connect_database(
            self._settings,
            application_name="bond_workflow_write",
        ) as connection:
            connection.execute(
                """
                INSERT INTO bond.demo_sessions (session_id)
                VALUES (%s)
                ON CONFLICT (session_id) DO NOTHING
                """,
                (session_id,),
            )

    def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        with connect_database(
            self._settings,
            application_name="bond_workflow_write",
        ) as connection:
            row = connection.execute(
                f"""
                INSERT INTO bond.improvements (
                    {_RECOMMENDATION_COLUMNS}
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING {_RECOMMENDATION_COLUMNS}
                """,
                (
                    recommendation.id,
                    recommendation.session_id,
                    recommendation.service_id,
                    recommendation.rule_id,
                    recommendation.rule_version,
                    recommendation.title,
                    recommendation.detail,
                    recommendation.owner,
                    recommendation.expected_result,
                    recommendation.status.value,
                    recommendation.created_at,
                    recommendation.updated_at,
                ),
            ).fetchone()
        if row is None:
            raise RuntimeError("The workflow repository did not return a recommendation.")
        return _recommendation(row)

    def get_recommendation(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> Recommendation | None:
        with connect_database(
            self._settings,
            application_name="bond_workflow_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            row = connection.execute(
                f"""
                SELECT {_RECOMMENDATION_COLUMNS}
                FROM bond.improvements
                WHERE id = %s AND session_id = %s
                """,
                (improvement_id, session_id),
            ).fetchone()
        return None if row is None else _recommendation(row)

    def list_recommendations(self, session_id: UUID) -> tuple[Recommendation, ...]:
        with connect_database(
            self._settings,
            application_name="bond_workflow_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            rows = connection.execute(
                f"""
                SELECT {_RECOMMENDATION_COLUMNS}
                FROM bond.improvements
                WHERE session_id = %s
                ORDER BY created_at DESC, id
                """,
                (session_id,),
            ).fetchall()
        return tuple(_recommendation(row) for row in rows)

    def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        with connect_database(
            self._settings,
            application_name="bond_workflow_write",
        ) as connection:
            row = connection.execute(
                f"""
                UPDATE bond.improvements
                SET status = %s,
                    updated_at = %s
                WHERE id = %s
                  AND session_id = %s
                RETURNING {_RECOMMENDATION_COLUMNS}
                """,
                (
                    recommendation.status.value,
                    recommendation.updated_at,
                    recommendation.id,
                    recommendation.session_id,
                ),
            ).fetchone()
        if row is None:
            raise ValueError("The recommendation does not exist in this session.")
        return _recommendation(row)

    def append_event(self, event: WorkflowEvent) -> WorkflowEvent | None:
        with connect_database(
            self._settings,
            application_name="bond_workflow_write",
        ) as connection:
            row = connection.execute(
                f"""
                INSERT INTO bond.workflow_events (
                    {_EVENT_COLUMNS}
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (improvement_id, request_id) DO NOTHING
                RETURNING {_EVENT_COLUMNS}
                """,
                (
                    event.id,
                    event.improvement_id,
                    event.session_id,
                    event.kind.value,
                    event.actor,
                    event.detail,
                    event.request_id,
                    event.occurred_at,
                ),
            ).fetchone()
        return None if row is None else _event(row)

    def find_event(
        self,
        improvement_id: UUID,
        request_id: UUID,
    ) -> WorkflowEvent | None:
        with connect_database(
            self._settings,
            application_name="bond_workflow_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            row = connection.execute(
                f"""
                SELECT {_EVENT_COLUMNS}
                FROM bond.workflow_events
                WHERE improvement_id = %s AND request_id = %s
                """,
                (improvement_id, request_id),
            ).fetchone()
        return None if row is None else _event(row)

    def list_events(
        self,
        improvement_id: UUID,
        session_id: UUID,
    ) -> tuple[WorkflowEvent, ...]:
        with connect_database(
            self._settings,
            application_name="bond_workflow_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            rows = connection.execute(
                f"""
                SELECT {_EVENT_COLUMNS}
                FROM bond.workflow_events
                WHERE improvement_id = %s AND session_id = %s
                ORDER BY occurred_at, id
                """,
                (improvement_id, session_id),
            ).fetchall()
        return tuple(_event(row) for row in rows)
