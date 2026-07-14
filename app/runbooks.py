from app.models import Incident, RunbookRecommendation


RUNBOOKS = {
    "payments": {
        "title": "Payments Failure Runbook",
        "steps": [
            "Confirm payment provider health and error rates.",
            "Compare failures with the latest payments deployment.",
            "Rollback the suspected change if failures began after deployment.",
            "Verify successful payment volume has recovered.",
        ],
    },
    "performance": {
        "title": "High Latency Runbook",
        "steps": [
            "Check latency percentiles and request volume.",
            "Identify saturated application dependencies.",
            "Scale the affected service or rollback the latest change.",
            "Verify latency has returned to its normal range.",
        ],
    },
    "database": {
        "title": "Database Incident Runbook",
        "steps": [
            "Check database availability and connection saturation.",
            "Review slow queries and recent schema changes.",
            "Rollback the suspected database change if safe.",
            "Verify application database errors have recovered.",
        ],
    },
    "unknown": {
        "title": "General Incident Triage Runbook",
        "steps": [
            "Confirm the affected service and customer symptoms.",
            "Review recent deployments and dependency health.",
            "Rollback the most suspicious recent change if safe.",
            "Verify the reported symptoms have recovered.",
        ],
    },
}


def find_runbook(incident: Incident) -> RunbookRecommendation:
    runbook = RUNBOOKS[incident.suspected_category]

    return RunbookRecommendation(
        incident_id=incident.id,
        title=runbook["title"],
        steps=runbook["steps"],
    )