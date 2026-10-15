"""Tests hosted workflow runtime selection without database credentials."""

import pytest

from bond.workflow_runtime import (
    MEMORY_MODE,
    POSTGRES_MODE,
    build_hosted_workflow_runtime,
)


def test_hosted_runtime_defaults_to_memory_without_database_settings() -> None:
    runtime = build_hosted_workflow_runtime({})

    assert runtime.mode is MEMORY_MODE


def test_hosted_runtime_requires_complete_database_settings() -> None:
    incomplete = {
        "BOND_DB_HOST": "database.example.com",
        "BOND_DB_USER": "bond_app",
    }

    runtime = build_hosted_workflow_runtime(incomplete)

    assert runtime.mode is MEMORY_MODE


def test_hosted_runtime_selects_postgres_with_required_settings() -> None:
    settings = {
        "BOND_DB_HOST": "database.example.com",
        "BOND_DB_PORT": "5432",
        "BOND_DB_NAME": "postgres",
        "BOND_DB_USER": "bond_app",
        "BOND_DB_PASSWORD": "not-a-real-password",
    }

    runtime = build_hosted_workflow_runtime(settings)

    assert runtime.mode is POSTGRES_MODE


def test_hosted_runtime_ignores_non_string_values() -> None:
    settings = {
        "BOND_DB_HOST": "database.example.com",
        "BOND_DB_USER": "bond_app",
        "BOND_DB_PASSWORD": 12345,
    }

    runtime = build_hosted_workflow_runtime(settings)

    assert runtime.mode is MEMORY_MODE


@pytest.mark.parametrize(
    ("missing_key", "settings"),
    [
        (
            "BOND_DB_HOST",
            {
                "BOND_DB_USER": "bond_app",
                "BOND_DB_PASSWORD": "not-a-real-password",
            },
        ),
        (
            "BOND_DB_USER",
            {
                "BOND_DB_HOST": "database.example.com",
                "BOND_DB_PASSWORD": "not-a-real-password",
            },
        ),
        (
            "BOND_DB_PASSWORD",
            {
                "BOND_DB_HOST": "database.example.com",
                "BOND_DB_USER": "bond_app",
            },
        ),
    ],
)
def test_hosted_runtime_falls_back_when_a_required_setting_is_missing(
    missing_key: str,
    settings: dict[str, str],
) -> None:
    runtime = build_hosted_workflow_runtime(settings)

    assert missing_key not in settings
    assert runtime.mode is MEMORY_MODE
