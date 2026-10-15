"""Selects the workflow storage mode without exposing credentials."""

from uuid import UUID

from bond.application_workflow import AssuranceWorkflow
from bond.config import DatabaseSettings
from bond.repositories.fixtures import FixtureCatalogRepository
from bond.repositories.memory import InMemoryWorkflowRepository
from bond.repositories.postgres_workflow import PostgresWorkflowRepository

MEMORY_MODE = "memory"
POSTGRES_MODE = "postgres"


class WorkflowRuntime:
    def __init__(self, application: AssuranceWorkflow, mode: str) -> None:
        self.application = application
        self.mode = mode

    def open_session(self, session_id: UUID) -> None:
        self.application.open_session(session_id)


def build_workflow_runtime(mode: str = MEMORY_MODE) -> WorkflowRuntime:
    catalog = FixtureCatalogRepository()

    if mode == MEMORY_MODE:
        return WorkflowRuntime(
            AssuranceWorkflow(catalog, InMemoryWorkflowRepository()),
            MEMORY_MODE,
        )

    if mode == POSTGRES_MODE:
        settings = DatabaseSettings.model_validate({})
        repository = PostgresWorkflowRepository(settings)
        return WorkflowRuntime(
            AssuranceWorkflow(catalog, repository),
            POSTGRES_MODE,
        )

    raise ValueError("Workflow storage mode must be memory or postgres.")
