"""Verifies restricted workflow permissions using disposable demo sessions."""

import os
from typing import LiteralString
from uuid import UUID, uuid4

from psycopg.errors import InsufficientPrivilege

from bond.application_workflow import AssuranceWorkflow
from bond.config import DatabaseSettings
from bond.domain.workflow import RecommendationDraft
from bond.infrastructure.database import connect_database
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.repositories.postgres_workflow import PostgresWorkflowRepository


def runtime_settings() -> DatabaseSettings:
    return DatabaseSettings.model_validate(
        {
            "host": os.environ["BOND_APP_DB_HOST"],
            "port": int(os.environ["BOND_APP_DB_PORT"]),
            "name": os.environ.get("BOND_APP_DB_NAME", "postgres"),
            "user": os.environ["BOND_APP_DB_USER"],
            "password": os.environ["BOND_APP_DB_PASSWORD"],
        }
    )


def expect_denied(
    settings: DatabaseSettings,
    session_id: UUID,
    statement: LiteralString,
    parameters: tuple[object, ...] = (),
) -> None:
    try:
        with connect_database(settings) as connection:
            try:
                connection.execute(
                    "SELECT set_config('bond.session_id', %s, true)",
                    (str(session_id),),
                )
                connection.execute(statement, parameters)
            finally:
                connection.rollback()
    except InsufficientPrivilege:
        return
    raise RuntimeError("An operation expected to be denied was permitted.")


def cleanup_sessions(
    settings: DatabaseSettings,
    sessions: tuple[UUID, UUID],
) -> None:
    failures = 0
    for session_id in sessions:
        try:
            with connect_database(settings) as connection:
                connection.execute(
                    "SELECT set_config('bond.session_id', %s, true)",
                    (str(session_id),),
                )
                connection.execute(
                    "DELETE FROM bond.demo_sessions WHERE session_id = %s",
                    (session_id,),
                )
                remaining = connection.execute(
                    "SELECT count(*) FROM bond.demo_sessions WHERE session_id = %s",
                    (session_id,),
                ).fetchone()
                if remaining != (0,):
                    raise RuntimeError("A test session remains after cleanup.")
        except Exception:
            failures += 1
    if failures:
        raise RuntimeError("Cleanup failed for one or more verification sessions.")
    print("Both verification sessions cleaned up: VERIFIED")


def main() -> int:
    settings = runtime_settings()
    application = AssuranceWorkflow(
        FixtureCatalogRepository(),
        PostgresWorkflowRepository(settings),
    )
    first_session, second_session = uuid4(), uuid4()

    with connect_database(settings) as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        identity = connection.execute(
            """
            SELECT current_user = 'bond_app',
                   NOT rolsuper AND NOT rolbypassrls
            FROM pg_roles
            WHERE rolname = current_user
            """
        ).fetchone()
    if identity != (True, True):
        raise RuntimeError("Verification requires the restricted bond_app identity.")
    print("Restricted role identity: VERIFIED")

    try:
        application.open_session(first_session)
        application.open_session(second_session)

        recommendation = application.propose(
            first_session,
            RecommendationDraft(
                service_id="billing_export",
                rule_id="ownership_assigned",
                rule_version="1",
                title="Restricted runtime isolation verification",
                detail="Disposable verification record, not a production action.",
                owner=None,
                expected_result="Only the owning session can access this record.",
            ),
            uuid4(),
        )

        if application.recommendation(recommendation.id, first_session) is None:
            raise RuntimeError("The owning session cannot read its recommendation.")
        if application.recommendation(recommendation.id, second_session) is not None:
            raise RuntimeError("The other session can read the recommendation.")

        events = application.history(recommendation.id, first_session)
        if len(events) != 1 or events[0].kind.value != "recommendation_created":
            raise RuntimeError("The creation event was not recorded as expected.")
        if application.history(recommendation.id, second_session):
            raise RuntimeError("The other session can read the event history.")
        print("Application session scoped workflow: VERIFIED")

        with connect_database(settings) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute(
                "SELECT set_config('bond.session_id', %s, true)",
                (str(second_session),),
            )
            hidden_recommendation = connection.execute(
                "SELECT id FROM bond.improvements WHERE id = %s",
                (recommendation.id,),
            ).fetchone()
            hidden_event = connection.execute(
                "SELECT id FROM bond.workflow_events WHERE improvement_id = %s",
                (recommendation.id,),
            ).fetchone()
        if hidden_recommendation is not None or hidden_event is not None:
            raise RuntimeError("RLS exposed another session's workflow rows.")
        print("RLS isolation without SQL session filters: VERIFIED")

        expect_denied(
            settings,
            first_session,
            "INSERT INTO bond.demo_sessions (session_id) VALUES (%s)",
            (uuid4(),),
        )
        print("Cross session insertion denied: VERIFIED")

        expect_denied(
            settings,
            first_session,
            "SELECT version FROM bond_meta.schema_migrations",
        )
        print("Migration metadata access denied: VERIFIED")

        expect_denied(
            settings,
            first_session,
            "UPDATE bond.audit_events SET event_type = event_type WHERE false",
        )
        expect_denied(
            settings,
            first_session,
            "DELETE FROM bond.audit_events WHERE false",
        )
        print("Audit update and delete privileges denied: VERIFIED")
    finally:
        cleanup_sessions(settings, (first_session, second_session))

    print("Restricted runtime verification: PASSED")
    print("No roles, policies, grants, or migrations changed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("RESTRICTED ROLE VERIFICATION FAILED")
        print("Exception type:", type(error).__name__)
        sqlstate = getattr(error, "sqlstate", None)
        if isinstance(sqlstate, str) and len(sqlstate) == 5 and sqlstate.isalnum():
            print("SQLSTATE:", sqlstate)
        print("Raw error text and configuration values were withheld.")
        raise SystemExit(1) from None
