"""Read only catalog adapter. Runtime permissions are configured separately."""

from bond.config import DatabaseSettings
from bond.domain.models import Service
from bond.infrastructure.database import connect_database


class PostgresCatalogRepository:
    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings

    def list_services(self) -> tuple[Service, ...]:
        with connect_database(
            self._settings,
            application_name="bond_catalog_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            rows = connection.execute(
                "SELECT document FROM bond.catalog ORDER BY service_id"
            ).fetchall()
        return tuple(Service.model_validate(row[0]) for row in rows)

    def get_service(self, service_id: str) -> Service | None:
        with connect_database(
            self._settings,
            application_name="bond_catalog_read",
        ) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            row = connection.execute(
                "SELECT document FROM bond.catalog WHERE service_id = %s",
                (service_id,),
            ).fetchone()
        return None if row is None else Service.model_validate(row[0])
