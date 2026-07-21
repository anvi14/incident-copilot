from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.ai_runbooks import recommend_runbook_for_incident
from app.database import initialize_database
from app.investigation import investigate_incident
from app.models import (
    AlertCreate,
    Incident,
    IncidentEvent,
    IncidentStatusUpdate,
    InvestigationResult,
    RunbookRecommendation,
)
from app.storage import (
    create_incident,
    create_incident_event,
    get_incident,
    list_incident_events,
    list_incidents,
    update_incident_status,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/alerts", response_model=Incident)
def receive_alert(alert: AlertCreate):
    return create_incident(alert)


@app.get("/incidents", response_model=list[Incident])
def get_incidents():
    return list_incidents()


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident_by_id(incident_id: int):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@app.get(
    "/incidents/{incident_id}/events",
    response_model=list[IncidentEvent],
)
def get_incident_events(incident_id: int):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return list_incident_events(incident_id)


@app.post(
    "/incidents/{incident_id}/investigate",
    response_model=InvestigationResult,
)
def investigate_incident_by_id(incident_id: int):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = investigate_incident(incident)

    create_incident_event(
        incident_id=incident_id,
        event_type="commit_suspected",
        message=(
            f"Suspected commit {result.suspected_commit_sha}: "
            f"{result.reason}"
        ),
    )

    return result


@app.get(
    "/incidents/{incident_id}/runbook",
    response_model=RunbookRecommendation,
)
def get_incident_runbook(incident_id: int):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    runbook = recommend_runbook_for_incident(incident)

    create_incident_event(
        incident_id=incident_id,
        event_type="runbook_recommended",
        message=f"Recommended runbook: {runbook.title}",
    )

    return runbook


@app.patch("/incidents/{incident_id}/status", response_model=Incident)
def change_incident_status(
    incident_id: int,
    status_update: IncidentStatusUpdate,
):
    incident = update_incident_status(
        incident_id,
        status_update.status,
    )

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident
