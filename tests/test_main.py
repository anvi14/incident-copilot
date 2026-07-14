import pytest
from fastapi.testclient import TestClient
from app import database

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database_path)

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_incident_from_alert(client):
    response = client.post(
        "/alerts",
        json={
            "service": "payments-api",
            "severity": "critical",
            "message": "Payment requests are failing",
        },
    )

    assert response.status_code == 200

    incident = response.json()
    assert incident["service"] == "payments-api"
    assert incident["severity"] == "critical"
    assert incident["status"] == "open"
    assert incident["suspected_category"] == "payments"

def test_list_incidents(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "checkout-api",
            "severity": "high",
            "message": "Checkout latency is increasing",
        },
    )
    created_incident = created_response.json()

    response = client.get("/incidents")

    assert response.status_code == 200

    incidents = response.json()
    assert len(incidents) == 1
    assert incidents[0]["id"] == created_incident["id"]
    assert incidents[0]["service"] == "checkout-api"


def test_get_incident_by_id(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "orders-api",
            "severity": "critical",
            "message": "Database connection failure",
        },
    )
    created_incident = created_response.json()

    response = client.get(f"/incidents/{created_incident['id']}")

    assert response.status_code == 200
    assert response.json() == created_incident


def test_get_unknown_incident_returns_404(client):
    response = client.get("/incidents/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Incident not found"}

def test_update_incident_status(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "payments-api",
            "severity": "critical",
            "message": "Payment requests are failing",
        },
    )
    incident_id = created_response.json()["id"]

    response = client.patch(
        f"/incidents/{incident_id}/status",
        json={"status": "investigating"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "investigating"


def test_update_unknown_incident_returns_404(client):
    response = client.patch(
        "/incidents/9999/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Incident not found"}


def test_reject_invalid_incident_status(client):
    response = client.patch(
        "/incidents/9999/status",
        json={"status": "done"},
    )

    assert response.status_code == 422

def test_new_incident_has_alert_received_event(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "payments-api",
            "severity": "critical",
            "message": "Payment requests are failing",
        },
    )
    incident_id = created_response.json()["id"]

    response = client.get(f"/incidents/{incident_id}/events")

    assert response.status_code == 200

    events = response.json()
    assert len(events) == 1
    assert events[0]["incident_id"] == incident_id
    assert events[0]["event_type"] == "alert_received"
    assert events[0]["message"] == "Payment requests are failing"
    assert "created_at" in events[0]


def test_status_change_adds_timeline_event(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "checkout-api",
            "severity": "high",
            "message": "Checkout latency is elevated",
        },
    )
    incident_id = created_response.json()["id"]

    client.patch(
        f"/incidents/{incident_id}/status",
        json={"status": "investigating"},
    )

    response = client.get(f"/incidents/{incident_id}/events")

    assert response.status_code == 200

    events = response.json()
    assert len(events) == 2
    assert events[1]["event_type"] == "status_changed"
    assert events[1]["message"] == "Status changed from open to investigating"


def test_investigate_incident_identifies_suspected_commit(client):
    created_response = client.post(
        "/alerts",
        json={
            "service": "payments-api",
            "severity": "critical",
            "message": "Payment requests are failing",
        },
    )
    incident_id = created_response.json()["id"]

    response = client.post(f"/incidents/{incident_id}/investigate")

    assert response.status_code == 200

    investigation = response.json()
    assert investigation["incident_id"] == incident_id
    assert investigation["suspected_commit_sha"] == "7f3a9c1"
    assert investigation["confidence"] == "high"
    assert "payment" in investigation["reason"].lower()

    events_response = client.get(f"/incidents/{incident_id}/events")
    events = events_response.json()

    assert len(events) == 2
    assert events[1]["event_type"] == "commit_suspected"
    assert "7f3a9c1" in events[1]["message"]
