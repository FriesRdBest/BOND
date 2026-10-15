"""Read only API contract checks."""

from fastapi.testclient import TestClient

from bond.api import app


def test_health_does_not_require_database_credentials() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "synthetic"}


def test_catalog_is_paginated() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/catalog", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_catalog_rejects_excessive_page_size() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/catalog", params={"limit": 101})
    assert response.status_code == 422


def test_unknown_service_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/catalog/not_present")
    assert response.status_code == 404


def test_scorecard_contract() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/scorecard")
    assert response.status_code == 200
    assert response.json()["summary"]["total"] == 18


def test_telemetry_contract_labels_synthetic_evidence() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/telemetry")
    assert response.status_code == 200
    assert response.json()["source"] == "synthetic"


def test_write_route_is_not_exposed() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/catalog")
    assert response.status_code == 405
