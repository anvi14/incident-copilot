
from app.models import Incident
from app.runbooks import (
    Runbook,
    find_runbook,
    load_runbooks,
    retrieve_runbooks,
)


def test_loads_runbook_from_markdown(tmp_path):
    runbook_file = tmp_path / "payments-failure.md"
    runbook_file.write_text(
        """---
id: payments-failure
title: Payments Failure Runbook
services:
  - payments-api
categories:
  - payments
severities:
  - critical
  - high
---
# Payments Failure Runbook

1. Confirm payment provider health and error rates.
2. Compare failures with the latest payments deployment.
""",
        encoding="utf-8",
    )

    runbooks = load_runbooks(tmp_path)

    assert len(runbooks) == 1

    runbook = runbooks[0]
    assert runbook.id == "payments-failure"
    assert runbook.title == "Payments Failure Runbook"
    assert runbook.services == ["payments-api"]
    assert runbook.categories == ["payments"]
    assert runbook.severities == ["critical", "high"]
    assert runbook.content == (
        "# Payments Failure Runbook\n\n"
        "1. Confirm payment provider health and error rates.\n"
        "2. Compare failures with the latest payments deployment.\n"
    )


def test_retrieves_most_relevant_runbook_first():
    incident = Incident(
        id=1,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing at the provider",
        status="open",
        suspected_category="payments",
    )
    payments_runbook = Runbook(
        id="payments-failure",
        title="Payments Failure Runbook",
        services=["payments-api"],
        categories=["payments"],
        severities=["critical", "high"],
        content=(
            "# Payments Failure Runbook\n\n"
            "Investigate failing payment requests and provider errors.\n"
        ),
    )
    database_runbook = Runbook(
        id="database-incident",
        title="Database Incident Runbook",
        services=["orders-api"],
        categories=["database"],
        severities=["critical"],
        content=(
            "# Database Incident Runbook\n\n"
            "Investigate database connections and slow queries.\n"
        ),
    )

    matches = retrieve_runbooks(
        incident,
        [database_runbook, payments_runbook],
    )

    assert [runbook.id for runbook in matches] == [
        "payments-failure",
        "database-incident",
    ]


def test_returns_only_approved_fallback_when_nothing_matches():
    incident = Incident(
        id=2,
        service="search-api",
        severity="medium",
        message="Search indexing has stopped",
        status="open",
        suspected_category="indexing",
    )
    payments_runbook = Runbook(
        id="payments-failure",
        title="Payments Failure Runbook",
        services=["payments-api"],
        categories=["payments"],
        severities=["critical"],
        content="# Payments Failure Runbook\n\nInvestigate provider errors.\n",
    )
    fallback_runbook = Runbook(
        id="general-triage",
        title="General Incident Triage Runbook",
        services=[],
        categories=[],
        severities=[],
        content=(
            "# General Incident Triage Runbook\n\n"
            "Confirm the affected service and customer symptoms.\n"
        ),
        is_fallback=True,
    )

    matches = retrieve_runbooks(
        incident,
        [payments_runbook, fallback_runbook],
    )

    assert [runbook.id for runbook in matches] == ["general-triage"]


def test_loads_fallback_setting_from_markdown(tmp_path):
    runbook_file = tmp_path / "general-triage.md"
    runbook_file.write_text(
        """---
id: general-triage
title: General Incident Triage Runbook
services:
categories:
severities:
is_fallback: true
---
# General Incident Triage Runbook

Confirm the affected service and customer symptoms.
""",
        encoding="utf-8",
    )

    runbooks = load_runbooks(tmp_path)

    assert len(runbooks) == 1
    assert runbooks[0].id == "general-triage"
    assert runbooks[0].is_fallback is True


def test_recommendation_uses_retrieved_approved_content():
    incident = Incident(
        id=3,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing",
        status="open",
        suspected_category="payments",
    )
    approved_content = (
        "# Payments Failure Runbook\n\n"
        "1. Confirm payment provider health and error rates.\n"
        "2. Compare failures with the latest payments deployment.\n"
    )
    payments_runbook = Runbook(
        id="payments-failure",
        title="Payments Failure Runbook",
        services=["payments-api"],
        categories=["payments"],
        severities=["critical"],
        content=approved_content,
    )

    recommendation = find_runbook(
        incident,
        [payments_runbook],
    )

    assert recommendation.incident_id == incident.id
    assert recommendation.title == payments_runbook.title
    assert recommendation.content == approved_content
