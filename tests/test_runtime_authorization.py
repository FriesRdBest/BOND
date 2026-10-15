"""Authorization migration and PostgreSQL session boundary contract tests."""

from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from bond.config import DatabaseSettings
from bond.domain.workflow import WorkflowEvent, WorkflowEventKind
from bond.infrastructure.migrations import load_migrations
from bond.repositories.postgres_workflow import PostgresWorkflowRepository


def settings() -> DatabaseSettings:
    return DatabaseSettings.model_validate(
        {
            "host": "example.invalid",
            "port": 5432,
            "name": "postgres",
            "user": "test_operator",
            "password": "synthetic_test_password",
        }
    )


def test_runtime_authorization_migration_is_present() -> None:
    migrations = load_migrations()
    assert [migration.version for migration in migrations] == [
        "0001_foundation.sql",
        "0002_assurance_workflow.sql",
        "0003_runtime_authorization.sql",
    ]


def test_runtime_authorization_migration_has_expected_boundaries() -> None:
    migrations = load_migrations()
    migration = next(
        item for item in migrations if item.version == "0003_runtime_authorization.sql"
    )
    sql = migration.statement

    assert "GRANT USAGE ON SCHEMA bond TO bond_app" in sql
    assert "GRANT SELECT ON bond.catalog TO bond_app" in sql
    assert "current_setting('bond.session_id', true)::uuid" in sql
    assert "CREATE POLICY runtime_session_isolation" in sql
    assert "CREATE POLICY runtime_recommendation_isolation" in sql
    assert "CREATE POLICY runtime_workflow_event_isolation" in sql
    assert "CREATE POLICY runtime_audit_event_isolation" in sql
    assert "bond_meta" not in sql.split("DO $$", 1)[1]


class FakeResult:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> list[tuple[Any, ...]]:
        return list(self._rows)


class FakeConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...] | None]] = []

    def execute(
        self,
        query: str,
        parameters: tuple[object, ...] | None = None,
    ) -> FakeResult:
        self.calls.append((query, parameters))
        return FakeResult([])

    @contextmanager
    def transaction(self):
        yield


@contextmanager
def fake_database_connection(connection: FakeConnection):
    yield connection


def test_ensure_session_binds_the_transaction_to_the_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    monkeypatch.setattr(
        "bond.repositories.postgres_workflow.connect_database",
        lambda *args, **kwargs: fake_database_connection(connection),
    )

    session_id = uuid4()
    repository = PostgresWorkflowRepository(settings())
    repository.ensure_session(session_id)

    assert connection.calls[0][0] == "SELECT set_config('bond.session_id', %s, true)"
    assert connection.calls[0][1] == (str(session_id),)
    assert "INSERT INTO bond.demo_sessions" in connection.calls[1][0]
    assert connection.calls[1][1] == (session_id,)


def test_recommendation_lookup_binds_and_scopes_the_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    monkeypatch.setattr(
        "bond.repositories.postgres_workflow.connect_database",
        lambda *args, **kwargs: fake_database_connection(connection),
    )

    improvement_id = uuid4()
    session_id = uuid4()
    repository = PostgresWorkflowRepository(settings())

    assert repository.get_recommendation(improvement_id, session_id) is None

    assert connection.calls[1][0] == "SELECT set_config('bond.session_id', %s, true)"
    assert connection.calls[1][1] == (str(session_id),)
    assert "WHERE id = %s AND session_id = %s" in connection.calls[2][0]
    assert connection.calls[2][1] == (improvement_id, session_id)


def test_event_insert_binds_and_scopes_the_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    monkeypatch.setattr(
        "bond.repositories.postgres_workflow.connect_database",
        lambda *args, **kwargs: fake_database_connection(connection),
    )

    session_id = uuid4()
    improvement_id = uuid4()
    request_id = uuid4()
    occurred_at = datetime.now(UTC)

    event = WorkflowEvent(
        id=uuid4(),
        improvement_id=improvement_id,
        session_id=session_id,
        kind=WorkflowEventKind.RECOMMENDATION_CREATED,
        actor="BOND",
        detail="Test event.",
        request_id=request_id,
        occurred_at=occurred_at,
    )

    repository = PostgresWorkflowRepository(settings())
    repository.append_event(event)

    assert connection.calls[0][0] == "SELECT set_config('bond.session_id', %s, true)"
    assert connection.calls[0][1] == (str(session_id),)
    assert "INSERT INTO bond.workflow_events" in connection.calls[1][0]
    assert connection.calls[1][1] == (
        event.id,
        event.improvement_id,
        event.session_id,
        event.kind.value,
        event.actor,
        event.detail,
        event.request_id,
        event.occurred_at,
    )
