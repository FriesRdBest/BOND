"""Transactional migrations with checksum drift detection."""

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Any, LiteralString, cast

import psycopg


@dataclass(frozen=True)
class Migration:
    version: str
    statement: str
    checksum: str


def load_migrations() -> tuple[Migration, ...]:
    directory = files("bond.data.migrations")
    resources = sorted(
        (resource for resource in directory.iterdir() if resource.name.endswith(".sql")),
        key=lambda resource: resource.name,
    )
    migrations: list[Migration] = []
    for resource in resources:
        raw = resource.read_bytes()
        migrations.append(
            Migration(
                version=resource.name,
                statement=raw.decode("utf-8"),
                checksum=sha256(raw).hexdigest(),
            )
        )
    if not migrations:
        raise RuntimeError("No packaged migrations were found.")
    return tuple(migrations)


def validate_history(
    migrations: tuple[Migration, ...],
    applied: dict[str, str],
) -> None:
    known = {migration.version: migration.checksum for migration in migrations}
    for version, checksum in applied.items():
        if version not in known:
            raise RuntimeError("Database contains an unknown migration version.")
        if known[version] != checksum:
            raise RuntimeError("An applied migration checksum has changed.")


def read_history(
    connection: psycopg.Connection[tuple[Any, ...]],
) -> dict[str, str]:
    row = connection.execute(
        "SELECT to_regclass('bond_meta.schema_migrations') IS NOT NULL"
    ).fetchone()
    if row != (True,):
        return {}
    rows = connection.execute(
        "SELECT version, checksum FROM bond_meta.schema_migrations ORDER BY version"
    ).fetchall()
    return {str(row[0]): str(row[1]) for row in rows}


def pending_migrations(
    connection: psycopg.Connection[tuple[Any, ...]],
) -> tuple[Migration, ...]:
    migrations = load_migrations()
    applied = read_history(connection)
    validate_history(migrations, applied)
    return tuple(migration for migration in migrations if migration.version not in applied)


def apply_migrations(
    connection: psycopg.Connection[tuple[Any, ...]],
) -> tuple[str, ...]:
    applied_versions: list[str] = []

    with connection.transaction():
        connection.execute("SET LOCAL lock_timeout = '10s'")
        connection.execute("SET LOCAL statement_timeout = '60s'")
        connection.execute("SELECT pg_advisory_xact_lock(45098011)")

        connection.execute(
            """
            CREATE SCHEMA IF NOT EXISTS bond_meta;
            REVOKE ALL ON SCHEMA bond_meta FROM PUBLIC;
            CREATE TABLE IF NOT EXISTS bond_meta.schema_migrations (
                version text PRIMARY KEY,
                checksum text NOT NULL CHECK (char_length(checksum) = 64),
                applied_at timestamptz NOT NULL DEFAULT now()
            );
            ALTER TABLE bond_meta.schema_migrations ENABLE ROW LEVEL SECURITY;
            REVOKE ALL ON bond_meta.schema_migrations FROM PUBLIC;
            """,
            prepare=False,
        )

        for migration in pending_migrations(connection):
            # SQL comes only from reviewed packaged resources, never request input.
            connection.execute(
                cast(LiteralString, migration.statement),
                prepare=False,
            )
            connection.execute(
                """
                INSERT INTO bond_meta.schema_migrations (version, checksum)
                VALUES (%s, %s)
                """,
                (migration.version, migration.checksum),
            )
            applied_versions.append(migration.version)

    return tuple(applied_versions)
