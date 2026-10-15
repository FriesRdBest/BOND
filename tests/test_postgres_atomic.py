"""Atomic PostgreSQL workflow transaction boundary checks."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from bond.config import DatabaseSettings
from bond.domain.workflow import Recommendation, WorkflowStatus
from bond.repositories.postgres_workflow import PostgresWorkflowRepository


class FakeResult:
    def __init__(self, row: tuple[object, ...]) -> None:
        self._row = row

    def fetchone(self) -> tuple[object, ...]:
        return self._row


class FakeTransaction:
    def __enter__(self) -> "FakeTransaction":
        return self

    def __exit__(self, *_: object) -> None:
        return None


class FakeConnection:
    def __init__(self) -> None:
        self.statements: list[tuple[str, tuple[object, ...]]] = []

    def execute(
        self,
        query: str,
        parameters: tuple[object, ...] = (),
    ) -> FakeResult:
        self.statements.append((query, parameters))
        if "INSERT INTO bond.improvements" in query:
            return FakeResult(
                (
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    parameters[3],
                    parameters[4],
                    parameters[5],
                    parameters[6],
                    parameters[7],
                    parameters[8],
                    parameters[9],
                    parameters[10],
                    parameters[11],
                )
            )
        if "INSERT INTO bond.workflow_events" in query:
            return FakeResult(
                (
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    parameters[3],
                    parameters[4],
                    parameters[5],
                    parameters[6],
                    parameters[7],
                )
            )
        if "FROM bond.improvements" in query:
            return FakeResult(
                (
                    uuid4(),
                    uuid4(),
                    "service",
                    "rule",
                    "1",
                    "title",
                    "detail",
                    "owner",
                    "expected",
                    "proposed",
                    datetime.now(UTC),
                    datetime.now(UTC),
                )
            )
        return FakeResult((uuid4(),))

    def transaction(self) -> FakeTransaction:
        return FakeTransaction()

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_: object) -> None:
        return None


@pytest.fixture()
def connection(
    monkeypatch: pytest.MonkeyPatch,
) -> FakeConnection:
    fake = FakeConnection()
    monkeypatch.setattr(
        "bond.repositories.postgres_workflow.connect_database",
        lambda *_args, **_kwargs: fake,
    )
    return fake


def recommendation() -> Recommendation:
    timestamp = datetime.now(UTC)
    return Recommendation(
        id=uuid4(),
        session_id=uuid4(),
        service_id="service",
        rule_id="rule",
        rule_version="1",
        title="Title",
        detail="Detail",
        owner="Owner",
        expected_result="Expected result",
        status=WorkflowStatus.PROPOSED,
        created_at=timestamp,
        updated_at=timestamp,
    )


def test_atomic_operations_share_one_connection(
    connection: FakeConnection,
) -> None:
    repository = PostgresWorkflowRepository(
        DatabaseSettings(
            host="database.invalid",
            user="bond_test",
            password="dummy-test-only",
        )
    )
    item = recommendation()

    with repository.atomic(item.session_id):
        repository.create_recommendation(item)
        repository.append_event(
            __import__("bond.domain.workflow", fromlist=["WorkflowEvent"]).WorkflowEvent(
                id=uuid4(),
                improvement_id=item.id,
                session_id=item.session_id,
                kind="recommendation_created",
                actor="BOND",
                detail="Created",
                request_id=uuid4(),
                occurred_at=datetime.now(UTC),
            )
        )

    connect_calls = [
        statement for statement, _ in connection.statements if "pg_advisory_xact_lock" in statement
    ]
    assert len(connect_calls) == 1
    assert any(
        "INSERT INTO bond.improvements" in statement for statement, _ in connection.statements
    )
    assert any(
        "INSERT INTO bond.workflow_events" in statement for statement, _ in connection.statements
    )


def test_atomic_failure_propagates_without_commit(
    connection: FakeConnection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = PostgresWorkflowRepository(
        DatabaseSettings(
            host="database.invalid",
            user="bond_test",
            password="dummy-test-only",
        )
    )
    item = recommendation()

    with pytest.raises(RuntimeError, match="Injected failure"):
        with repository.atomic(item.session_id):
            repository.create_recommendation(item)
            raise RuntimeError("Injected failure")

    assert _import_active_connection() is None
    assert any(
        "INSERT INTO bond.improvements" in statement for statement, _ in connection.statements
    )


def _import_active_connection() -> Any:
    from bond.repositories.postgres_workflow import _ACTIVE_CONNECTION

    return _ACTIVE_CONNECTION.get()
