from app.database import get_connection
from app.models import AlertCreate, Incident, IncidentEvent, IncidentStatus


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
    status = "open"
    suspected_category = guess_category(alert.message)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO incidents (
                service,
                severity,
                message,
                status,
                suspected_category
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                alert.service,
                alert.severity,
                alert.message,
                status,
                suspected_category,
            ),
        )

        incident_id = cursor.lastrowid
    create_incident_event(
        incident_id=incident_id,
        event_type="alert_received",
        message=alert.message,
    )

    return Incident(
        id=incident_id,
        service=alert.service,
        severity=alert.severity,
        message=alert.message,
        status=status,
        suspected_category=suspected_category,
    )


def list_incidents() -> list[Incident]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM incidents ORDER BY id"
        ).fetchall()

    return [Incident(**dict(row)) for row in rows]


def get_incident(incident_id: int) -> Incident | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,),
        ).fetchone()

    if row is None:
        return None

    return Incident(**dict(row))

def update_incident_status(
    incident_id: int,
    status: IncidentStatus,
) -> Incident | None:
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            (status, incident_id),
        )

    if cursor.rowcount == 0:
        return None

    return get_incident(incident_id)

def create_incident_event(
    incident_id: int,
    event_type: str,
    message: str,
) -> IncidentEvent:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO incident_events (
                incident_id,
                event_type,
                message
            )
            VALUES (?, ?, ?)
            """,
            (incident_id, event_type, message),
        )

        row = connection.execute(
            "SELECT * FROM incident_events WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return IncidentEvent(**dict(row))


def list_incident_events(incident_id: int) -> list[IncidentEvent]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM incident_events
            WHERE incident_id = ?
            ORDER BY created_at, id
            """,
            (incident_id,),
        ).fetchall()

    return [IncidentEvent(**dict(row)) for row in rows]
