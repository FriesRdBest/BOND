"""Framework independent repository contracts."""

from typing import Protocol

from bond.domain.models import Service


class CatalogRepository(Protocol):
    def list_services(self) -> tuple[Service, ...]: ...

    def get_service(self, service_id: str) -> Service | None: ...
