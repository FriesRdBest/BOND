"""Read only deterministic catalog adapter."""

from importlib.resources import files

from pydantic import TypeAdapter

from bond.domain.models import Service

CATALOG_ADAPTER = TypeAdapter(tuple[Service, ...])


class FixtureCatalogRepository:
    def __init__(self) -> None:
        resource = files("bond.data").joinpath("catalog.json")
        self._services = CATALOG_ADAPTER.validate_json(resource.read_text(encoding="utf-8"))
        identifiers = {service.id for service in self._services}
        if len(identifiers) != len(self._services):
            raise ValueError("Catalog identifiers must be unique.")
        for service in self._services:
            if service.id in service.dependencies:
                raise ValueError("Services cannot depend on themselves.")
            if any(dependency not in identifiers for dependency in service.dependencies):
                raise ValueError("Every dependency must reference a catalog service.")

    def list_services(self) -> tuple[Service, ...]:
        return self._services

    def get_service(self, service_id: str) -> Service | None:
        return next((service for service in self._services if service.id == service_id), None)
