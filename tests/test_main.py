from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_incident_from_alert():
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