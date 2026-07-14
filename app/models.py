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

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus