"""Read only PostgreSQL security and integrity audit for BOND."""

import json
from typing import Any

from psycopg.rows import dict_row

from bond.config import DatabaseSettings
from bond.infrastructure.database import connect_database


def _rows(
    connection: Any,
    query: str,
) -> list[dict[str, Any]]:
    cursor = connection.cursor(row_factory=dict_row)
    cursor.execute(query)
    return cursor.fetchall()


def main() -> int:
    settings = DatabaseSettings()

    with connect_database(settings) as connection:
        connection.execute("SET TRANSACTION READ ONLY")

        bond_roles = _rows(
            connection,
            """
            SELECT rolname, rolsuper, rolcreaterole, rolcreatedb,
                   rolbypassrls, rolcanlogin, rolreplication
            FROM pg_roles
            WHERE rolname LIKE 'bond%'
            ORDER BY rolname
            """,
        )
        table_security = _rows(
            connection,
            """
            SELECT n.nspname AS schema_name,
                   c.relname AS table_name,
                   c.relrowsecurity AS rls_enabled,
                   c.relforcerowsecurity AS rls_forced,
                   pg_get_userbyid(c.relowner) AS owner
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('bond', 'bond_meta')
              AND c.relkind = 'r'
            ORDER BY n.nspname, c.relname
            """,
        )
        policies = _rows(
            connection,
            """
            SELECT schemaname, tablename, policyname, roles, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname IN ('bond', 'bond_meta')
            ORDER BY schemaname, tablename, policyname
            """,
        )
        public_grants = _rows(
            connection,
            """
            SELECT grantee, table_schema, table_name, privilege_type
            FROM information_schema.table_privileges
            WHERE table_schema IN ('bond', 'bond_meta')
              AND grantee IN ('PUBLIC', 'anon', 'authenticated')
            ORDER BY grantee, table_schema, table_name, privilege_type
            """,
        )
        role_grants = _rows(
            connection,
            """
            SELECT grantee, table_schema, table_name, privilege_type
            FROM information_schema.table_privileges
            WHERE table_schema IN ('bond', 'bond_meta')
              AND grantee LIKE 'bond%'
            ORDER BY grantee, table_schema, table_name, privilege_type
            """,
        )
        constraints = _rows(
            connection,
            """
            SELECT n.nspname AS schema_name,
                   cl.relname AS table_name,
                   con.conname AS constraint_name,
                   con.contype AS constraint_type,
                   pg_get_constraintdef(con.oid) AS definition
            FROM pg_constraint AS con
            JOIN pg_class AS cl ON cl.oid = con.conrelid
            JOIN pg_namespace AS n ON n.oid = cl.relnamespace
            WHERE n.nspname IN ('bond', 'bond_meta')
            ORDER BY n.nspname, cl.relname, con.conname
            """,
        )
        indexes = _rows(
            connection,
            """
            SELECT n.nspname AS schema_name,
                   cl.relname AS table_name,
                   ix.relname AS index_name,
                   pg_get_indexdef(ix.oid) AS definition
            FROM pg_index AS i
            JOIN pg_class AS ix ON ix.oid = i.indexrelid
            JOIN pg_class AS cl ON cl.oid = i.indrelid
            JOIN pg_namespace AS n ON n.oid = cl.relnamespace
            WHERE n.nspname IN ('bond', 'bond_meta')
            ORDER BY n.nspname, cl.relname, ix.relname
            """,
        )
        extensions = _rows(
            connection,
            """
            SELECT extname, extversion
            FROM pg_extension
            ORDER BY extname
            """,
        )

    report = {
        "bond_roles": bond_roles,
        "bond_table_security": table_security,
        "bond_policies": policies,
        "bond_public_grants": public_grants,
        "bond_role_grants": role_grants,
        "bond_constraints": constraints,
        "bond_indexes": indexes,
        "bond_extensions": extensions,
    }

    print(json.dumps(report, indent=2, sort_keys=True, default=str))

    print("\n=== AUDIT SUMMARY ===")
    print("Bond roles inspected:", len(bond_roles))
    print("Bond tables inspected:", len(table_security))
    print("Row level security policies:", len(policies))
    print("Public or API role table grants:", len(public_grants))
    print("Bond role table grants:", len(role_grants))
    print("Constraints inspected:", len(constraints))
    print("Indexes inspected:", len(indexes))

    if not policies:
        print("RESULT: No row level security policies are defined.")
    else:
        print("RESULT: Row level security policies are defined; review their scope.")

    if public_grants:
        print("RESULT: Public or API role table grants exist; review their scope.")
    else:
        print("RESULT: No public or API role table grants were found.")

    print("This audit is read only. It does not certify security or authorize changes.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("DATABASE SECURITY AUDIT FAILED")
        print("Exception type:", type(error).__name__)
        sqlstate = getattr(error, "sqlstate", None)
        if isinstance(sqlstate, str) and len(sqlstate) == 5 and sqlstate.isalnum():
            print("SQLSTATE:", sqlstate)
        print("Raw error text and configuration values were withheld.")
        raise SystemExit(1) from error
