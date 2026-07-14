from pydantic import BaseModel


class AlertCreate(BaseModel):
    service: str
    severity: str
    message: str


class Incident(BaseModel):
    id: int
    service: str
    severity: str
    message: str
    status: str
    suspected_category: str