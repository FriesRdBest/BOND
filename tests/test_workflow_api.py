"""API contract tests for the controlled assurance workflow."""

from uuid import uuid4

from fastapi.testclient import TestClient

from bond.api import app

client = TestClient(app)


def recommendation_payload(session_id, request_id):
    return {
        "session_id": str(session_id),
        "request_id": str(request_id),
        "service_id": "billing_export",
        "rule_id": "critical_vulnerabilities",
        "title": "Review billing export vulnerabilities",
        "detail": "Critical vulnerability evidence requires review.",
        "expected_result": "No critical vulnerabilities remain in the evidence.",
    }


def test_health_reports_synthetic_mode_and_memory_store():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "mode": "synthetic",
        "workflow_store": "memory",
    }


def test_complete_api_workflow_is_idempotent():
    session_id = uuid4()
    opened = client.post(
        "/api/v1/workflow/sessions",
        json={"session_id": str(session_id)},
    )
    assert opened.status_code == 204

    created = client.post(
        "/api/v1/workflow/recommendations",
        json=recommendation_payload(session_id, uuid4()),
    )
    assert created.status_code == 200
    recommendation = created.json()
    assert recommendation["status"] == "proposed"

    improvement_id = recommendation["id"]
    approval_request = {
        "session_id": str(session_id),
        "request_id": str(uuid4()),
        "actor": "Platform Owner",
        "reason": "The contract publication is appropriate.",
    }

    approved = client.post(
        f"/api/v1/workflow/recommendations/{improvement_id}/approval",
        json=approval_request,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    repeated = client.post(
        f"/api/v1/workflow/recommendations/{improvement_id}/approval",
        json=approval_request,
    )
    assert repeated.status_code == 200
    assert repeated.json() == approved.json()

    executed = client.post(
        f"/api/v1/workflow/recommendations/{improvement_id}/execution",
        json={
            "session_id": str(session_id),
            "request_id": str(uuid4()),
            "actor": "Automation",
            "simulated_command": "publish_contract_documentation",
            "reason": "The action is simulated in this demonstration.",
        },
    )
    assert executed.status_code == 200
    assert executed.json()["status"] == "executed"

    verified = client.post(
        f"/api/v1/workflow/recommendations/{improvement_id}/verification",
        json={
            "session_id": str(session_id),
            "request_id": str(uuid4()),
            "actor": "Reviewer",
            "observed_result": "The contract evidence is visible.",
            "passed": True,
            "reason": "The expected result was observed.",
        },
    )
    assert verified.status_code == 200
    assert verified.json()["status"] == "verified"

    events = client.get(
        f"/api/v1/workflow/recommendations/{improvement_id}/events",
        params={"session_id": str(session_id)},
    )
    assert events.status_code == 200
    assert [event["kind"] for event in events.json()] == [
        "recommendation_created",
        "approval_granted",
        "simulated_execution_recorded",
        "verification_passed",
    ]


def test_execution_before_approval_is_rejected():
    session_id = uuid4()
    client.post(
        "/api/v1/workflow/sessions",
        json={"session_id": str(session_id)},
    )
    created = client.post(
        "/api/v1/workflow/recommendations",
        json=recommendation_payload(session_id, uuid4()),
    )
    improvement_id = created.json()["id"]

    response = client.post(
        f"/api/v1/workflow/recommendations/{improvement_id}/execution",
        json={
            "session_id": str(session_id),
            "request_id": str(uuid4()),
            "actor": "Automation",
            "simulated_command": "publish_contract_documentation",
            "reason": "Attempted before approval.",
        },
    )
    assert response.status_code == 422
    assert "cannot move" in response.json()["detail"]


def test_cross_session_recommendation_is_not_found():
    session_id = uuid4()
    other_session = uuid4()
    client.post(
        "/api/v1/workflow/sessions",
        json={"session_id": str(session_id)},
    )
    created = client.post(
        "/api/v1/workflow/recommendations",
        json=recommendation_payload(session_id, uuid4()),
    )
    improvement_id = created.json()["id"]

    response = client.get(
        f"/api/v1/workflow/recommendations/{improvement_id}",
        params={"session_id": str(other_session)},
    )
    assert response.status_code == 404
