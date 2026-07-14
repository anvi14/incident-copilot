from datetime import datetime
from typing import Literal

from pydantic import BaseModel

IncidentStatus = Literal["open", "investigating", "mitigated", "resolved"]


class AlertCreate(BaseModel):
    service: str
    severity: str
    message: str


class Incident(BaseModel):
    id: int
    service: str
    severity: str
    message: str
    status: IncidentStatus
    suspected_category: str


class IncidentEvent(BaseModel):
    id: int
    incident_id: int
    event_type: str
    message: str
    created_at: datetime


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class InvestigationResult(BaseModel):
    incident_id: int
    suspected_commit_sha: str
    confidence: Literal["low", "medium", "high"]
    reason: str
