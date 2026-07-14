from app.models import AlertCreate, Incident

incidents: list[Incident] = []


def guess_category(message: str) -> str:
    lower_message = message.lower()

    if "payment" in lower_message:
        return "payments"
    if "latency" in lower_message or "slow" in lower_message:
        return "performance"
    if "database" in lower_message or "db" in lower_message:
        return "database"

    return "unknown"


def create_incident(alert: AlertCreate) -> Incident:
    incident = Incident(
        id=len(incidents) + 1,
        service=alert.service,
        severity=alert.severity,
        message=alert.message,
        status="open",
        suspected_category=guess_category(alert.message),
    )

    incidents.append(incident)
    return incident


def list_incidents() -> list[Incident]:
    return incidents

def get_incident(incident_id: int) -> Incident | None:
    for incident in incidents:
        if incident.id == incident_id:
            return incident
    return None