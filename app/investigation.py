from app.models import Incident, InvestigationResult


SIMULATED_COMMITS = {
    "payments": {
        "sha": "7f3a9c1",
        "confidence": "high",
        "reason": (
            "A recent payment validation change matches "
            "the incident's payment failure symptoms."
        ),
    },
    "performance": {
        "sha": "3d8e2b4",
        "confidence": "medium",
        "reason": (
            "A recent request-processing change may explain "
            "the reported latency."
        ),
    },
    "database": {
        "sha": "9c4b1e6",
        "confidence": "high",
        "reason": (
            "A recent database connection change matches "
            "the incident symptoms."
        ),
    },
    "unknown": {
        "sha": "1a2b3c4",
        "confidence": "low",
        "reason": (
            "The latest service change is a weak match because "
            "the incident category is unknown."
        ),
    },
}


def investigate_incident(incident: Incident) -> InvestigationResult:
    candidate = SIMULATED_COMMITS[incident.suspected_category]

    return InvestigationResult(
        incident_id=incident.id,
        suspected_commit_sha=candidate["sha"],
        confidence=candidate["confidence"],
        reason=candidate["reason"],
    )