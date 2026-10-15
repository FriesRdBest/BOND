"""Read only synthetic API. No administrative database access."""

from fastapi import FastAPI, HTTPException, Query

from bond.application import CatalogApplication, OrganizationSnapshot, ServiceAssessment
from bond.demo import WarehouseWindow, warehouse_fixture
from bond.repositories.fixtures import FixtureCatalogRepository

app = FastAPI(
    title="BOND assurance API",
    version="0.1.0",
    description=(
        "Independent portfolio demonstration. Read only synthetic evidence. "
        "No production infrastructure actions."
    ),
)

application = CatalogApplication(FixtureCatalogRepository())


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok", "mode": "synthetic"}


@app.get("/api/v1/scorecard", response_model=OrganizationSnapshot)
def scorecard() -> OrganizationSnapshot:
    return application.snapshot()


@app.get("/api/v1/catalog", response_model=list[ServiceAssessment])
def catalog(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServiceAssessment]:
    return list(application.snapshot().assessments[offset : offset + limit])


@app.get("/api/v1/catalog/{service_id}", response_model=ServiceAssessment)
def service_detail(service_id: str) -> ServiceAssessment:
    assessment = application.assess(service_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    return assessment


@app.get("/api/v1/telemetry", response_model=WarehouseWindow)
def telemetry() -> WarehouseWindow:
    return warehouse_fixture()
