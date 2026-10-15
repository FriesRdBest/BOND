"""Explicit database operator commands with redacted failure reporting."""

import argparse
import sys

from psycopg.types.json import Jsonb

from bond.config import DatabaseSettings
from bond.infrastructure.database import connect_database
from bond.infrastructure.migrations import (
    apply_migrations,
    pending_migrations,
    read_history,
)
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.repositories.postgres import PostgresCatalogRepository


def main() -> int:
    parser = argparse.ArgumentParser(description="BOND database operator")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--plan", action="store_true")
    actions.add_argument("--apply", action="store_true")
    actions.add_argument("--seed", action="store_true")
    actions.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    stage = "configuration"

    try:
        settings = DatabaseSettings()

        if arguments.plan:
            stage = "migration plan"
            with connect_database(settings) as connection:
                connection.execute("SET TRANSACTION READ ONLY")
                pending = pending_migrations(connection)
            print("Pending migrations:", len(pending))
            for migration in pending:
                print("PENDING:", migration.version)
            print("Plan only. No database changes made.")

        elif arguments.apply:
            stage = "migration transaction"
            with connect_database(settings) as connection:
                applied = apply_migrations(connection)
            print("Migration transaction committed.")
            print("Migrations applied:", len(applied))
            for version in applied:
                print("APPLIED:", version)

        elif arguments.seed:
            stage = "synthetic catalog seed"
            services = FixtureCatalogRepository().list_services()

            with connect_database(settings) as connection:
                connection.execute("SET LOCAL statement_timeout = '30s'")
                connection.execute("SELECT pg_advisory_xact_lock(45098012)")
                with connection.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO bond.catalog (service_id, document)
                        VALUES (%s, %s)
                        ON CONFLICT (service_id) DO UPDATE
                        SET document = EXCLUDED.document, updated_at = now()
                        WHERE bond.catalog.document IS DISTINCT FROM EXCLUDED.document
                        """,
                        [
                            (service.id, Jsonb(service.model_dump(mode="json")))
                            for service in services
                        ],
                    )
            print("Synthetic catalog seed committed:", len(services), "services.")
            print("No session or audit event records were created or deleted.")

        elif arguments.verify:
            stage = "schema verification"
            with connect_database(settings) as connection:
                connection.execute("SET TRANSACTION READ ONLY")
                pending = pending_migrations(connection)
                history = read_history(connection)
                rows = connection.execute(
                    """
                    SELECT c.relname, c.relrowsecurity
                    FROM pg_class AS c
                    JOIN pg_namespace AS n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'bond' AND c.relkind = 'r'
                    ORDER BY c.relname
                    """
                ).fetchall()

            expected_tables = {
                "audit_events",
                "catalog",
                "demo_sessions",
                "improvements",
                "workflow_events",
            }
            actual_tables = {str(row[0]) for row in rows}

            if pending:
                raise RuntimeError("There are unapplied migrations.")
            if actual_tables != expected_tables:
                raise RuntimeError("The initial table inventory differs from expectations.")
            if not all(row[1] is True for row in rows):
                raise RuntimeError("A BOND table does not have row security enabled.")

            stage = "persisted fixture verification"
            repository = PostgresCatalogRepository(settings)
            persisted = repository.list_services()
            fixtures = FixtureCatalogRepository().list_services()

            if sorted(persisted, key=lambda item: item.id) != sorted(
                fixtures, key=lambda item: item.id
            ):
                raise RuntimeError("Persisted catalog differs from the expected fixtures.")

            if repository.get_service("not_present") is not None:
                raise RuntimeError("Missing service lookup returned an unexpected value.")

            for fixture in fixtures:
                if repository.get_service(fixture.id) != fixture:
                    raise RuntimeError("Service lookup differs from its fixture.")

            print("Migration checksums: VERIFIED")
            print("Applied migration count:", len(history))
            print("Expected tables: VERIFIED")
            print("Row security enabled on all BOND tables: VERIFIED")
            print("Persisted synthetic services:", len(persisted))
            print("Catalog listing and individual lookups: VERIFIED")
            print("Restricted runtime role and public session policies: STILL PENDING")

        return 0

    except Exception as error:
        print("DATABASE OPERATOR FAILED")
        print("Stage:", stage)
        print("Exception type:", type(error).__name__)
        sqlstate = getattr(error, "sqlstate", None)
        if isinstance(sqlstate, str) and len(sqlstate) == 5 and sqlstate.isalnum():
            print("SQLSTATE:", sqlstate)
        print("Raw error text and configuration values were withheld.")
        print("Stop here and report this output. Do not change credentials blindly.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
