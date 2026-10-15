"""Local configuration and migration contract tests without database access."""

import pytest
from pydantic import ValidationError

from bond.config import DatabaseSettings
from bond.infrastructure.migrations import load_migrations, validate_history


def settings(**overrides: object) -> DatabaseSettings:
    values: dict[str, object] = {
        "host": "example.invalid",
        "port": 5432,
        "name": "postgres",
        "user": "test_operator",
        "password": "synthetic_test_password",
    }
    values.update(overrides)
    return DatabaseSettings.model_validate(values)


def test_credentials_are_not_in_settings_representation() -> None:
    configuration = settings()
    representation = repr(configuration)
    assert "synthetic_test_password" not in representation
    assert "test_operator" not in representation
    assert "example.invalid" not in representation


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_database_port_is_rejected(port: int) -> None:
    with pytest.raises(ValidationError):
        settings(port=port)


def test_empty_password_is_rejected() -> None:
    with pytest.raises(ValidationError):
        settings(password="")


def test_migration_resources_have_stable_checksums() -> None:
    first = load_migrations()
    second = load_migrations()
    assert first == second
    assert len(first) == 2
    assert len(first[0].checksum) == 64


def test_matching_history_is_accepted() -> None:
    migrations = load_migrations()
    validate_history(
        migrations,
        {migration.version: migration.checksum for migration in migrations},
    )


def test_changed_migration_is_rejected() -> None:
    migrations = load_migrations()
    with pytest.raises(RuntimeError, match="checksum"):
        validate_history(migrations, {migrations[0].version: "0" * 64})


def test_unknown_migration_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="unknown"):
        validate_history(load_migrations(), {"unknown.sql": "0" * 64})
