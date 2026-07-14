from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.database import initialize_database

from app.models import AlertCreate, Incident, IncidentStatusUpdate
from app.storage import (
    create_incident,
    get_incident,
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