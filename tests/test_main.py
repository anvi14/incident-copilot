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