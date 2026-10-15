"""Selects the workflow storage mode without exposing credentials."""

from collections.abc import Mapping
from uuid import UUID

from bond.application_workflow import AssuranceWorkflow
from bond.config import DatabaseSettings
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.repositories.memory import InMemoryWorkflowRepository
from bond.repositories.postgres_workflow import PostgresWorkflowRepository

MEMORY_MODE = "memory"
POSTGRES_MODE = "postgres"

REQUIRED_DATABASE_SETTINGS = (
    "BOND_DB_HOST",
    "BOND_DB_USER",
    "BOND_DB_PASSWORD",
)


class WorkflowRuntime:
    def __init__(self, application: AssuranceWorkflow, mode: str) -> None:
        self.application = application
        self.mode = mode

    def open_session(self, session_id: UUID) -> None:
        self.application.open_session(session_id)


def build_workflow_runtime(
    mode: str = MEMORY_MODE,
    database_settings: Mapping[str, str] | None = None,
) -> WorkflowRuntime:
    catalog = FixtureCatalogRepository()

    if mode == MEMORY_MODE:
        return WorkflowRuntime(
            AssuranceWorkflow(catalog, InMemoryWorkflowRepository()),
            MEMORY_MODE,
        )

    if mode == POSTGRES_MODE:
        settings = DatabaseSettings.model_validate(database_settings or {})
        repository = PostgresWorkflowRepository(settings)
        return WorkflowRuntime(
            AssuranceWorkflow(catalog, repository),
            POSTGRES_MODE,
        )

    raise ValueError("Workflow storage mode must be memory or postgres.")


def build_hosted_workflow_runtime(source: Mapping[str, str]) -> WorkflowRuntime:
    """Select durable PostgreSQL mode only when restricted settings are supplied."""

    database_settings = {
        key: value
        for key, value in source.items()
        if key.startswith("BOND_DB_") and isinstance(value, str)
    }

    if all(key in database_settings for key in REQUIRED_DATABASE_SETTINGS):
        return build_workflow_runtime(
            POSTGRES_MODE,
            database_settings=database_settings,
        )

    return build_workflow_runtime(MEMORY_MODE)
