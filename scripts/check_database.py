"""Read only connection verification with separate transport observations."""

import os
import sys
from importlib.resources import files

import psycopg

REQUIRED = (
    "BOND_DB_HOST",
    "BOND_DB_PORT",
    "BOND_DB_NAME",
    "BOND_DB_USER",
    "BOND_DB_PASSWORD",
)


def main() -> int:
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        print("DATABASE CHECK BLOCKED: Missing names:", ", ".join(missing))
        return 1

    password = os.environ["BOND_DB_PASSWORD"]
    if password.strip().lower() in {
        "[your-password]",
        "your-password",
        "your actual database password, entered exactly as created",
        "changeme",
    }:
        print("DATABASE CHECK BLOCKED: Password is a placeholder.")
        return 1

    certificate = files("bond.data").joinpath("supabase-ca.crt")
    if not certificate.is_file():
        print("DATABASE CHECK BLOCKED: Packaged CA certificate is missing.")
        return 1

    stage = "connection"

    try:
        with psycopg.connect(
            host=os.environ["BOND_DB_HOST"],
            port=int(os.environ["BOND_DB_PORT"]),
            dbname=os.environ["BOND_DB_NAME"],
            user=os.environ["BOND_DB_USER"],
            password=password,
            sslmode="verify-full",
            sslrootcert=str(certificate),
            connect_timeout=15,
            application_name="bond_foundation_check",
        ) as connection:
            print("Authentication: PASSED")
            print("Client TLS with certificate and hostname verification: PASSED")

            stage = "read only health query"

            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SELECT 1")

                if cursor.fetchone() != (1,):
                    print("DATABASE CHECK FAILED: Unexpected health query response.")
                    return 1

                print("Read only health query: PASSED")

                stage = "pooler upstream observation"

                cursor.execute("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
                observation = cursor.fetchone()

                if observation == (True,):
                    print("Pooler to PostgreSQL transport: REPORTED AS TLS")
                elif observation == (False,):
                    print("Pooler to PostgreSQL transport: NOT REPORTED AS TLS")
                    print(
                        "This describes the separate upstream connection, "
                        "not the verified client connection."
                    )
                    print(
                        "Retain this observation for the security review. "
                        "Do not claim every connection uses TLS."
                    )
                else:
                    print("Pooler to PostgreSQL transport: NO OBSERVATION AVAILABLE")

        print("DATABASE CONNECTION CHECK PASSED")
        print("No schema or application data was changed.")
        print("Runtime permissions and complete deployment security remain unverified.")
        return 0

    except Exception as error:
        print("DATABASE CHECK FAILED")
        print("Failure stage:", stage)
        print("Exception type:", type(error).__name__)

        message = str(error).lower()

        if "certificate" in message:
            print("Category: CERTIFICATE VALIDATION OR CONFIGURATION")
        elif "password authentication failed" in message:
            print("Category: AUTHENTICATION REJECTED")
        elif "tenant or user not found" in message:
            print("Category: POOLER ROUTING")
        elif "timeout" in message or "timed out" in message:
            print("Category: CONNECTION TIMEOUT")
        elif "permission denied" in message:
            print("Category: DATABASE PERMISSION")
        else:
            print("Category: REQUIRES FURTHER DIAGNOSIS")

        print("Raw error text and connection values were withheld.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
