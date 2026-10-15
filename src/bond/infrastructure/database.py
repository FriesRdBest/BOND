"""Verified TLS connection factory for operator and repository use."""

from importlib.resources import files
from typing import Any

import psycopg

from bond.config import DatabaseSettings


def connect_database(
    settings: DatabaseSettings,
    *,
    application_name: str = "bond_operator",
) -> psycopg.Connection[tuple[Any, ...]]:
    certificate = files("bond.data").joinpath("supabase-ca.crt")
    if not certificate.is_file():
        raise RuntimeError("The packaged database CA certificate is missing.")

    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.name,
        user=settings.user,
        password=settings.password.get_secret_value(),
        sslmode="verify-full",
        sslrootcert=str(certificate),
        connect_timeout=15,
        application_name=application_name,
        prepare_threshold=None,
    )
