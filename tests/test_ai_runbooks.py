from unittest.mock import Mock

from app.ai_runbooks import (
    AIRunbookSelection,
    recommend_runbook,
    recommend_runbook_for_incident,
    select_runbook_with_ai,
)
from app.models import Incident
from app.runbooks import Runbook


def make_incident() -> Incident:
    return Incident(
        id=1,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing",
        status="open",
        suspected_category="payments",
    )


def make_payments_runbook() -> Runbook:
    return Runbook(
        id="payments-failure",
        title="Payments Failure Runbook",
        services=["payments-api"],
        categories=["payments"],
        severities=["critical"],
        content="# Payments Failure Runbook\n\nApproved steps.\n",
    )


def test_ai_selects_approved_runbook():
    incident = make_incident()
    payments_runbook = make_payments_runbook()

    expected_selection = AIRunbookSelection(
        runbook_id="payments-failure",
        confidence="high",
        reason="The retrieved runbook matches the incident.",
    )

    client = Mock()
    client.responses.parse.return_value.output_parsed = expected_selection

    selection = select_runbook_with_ai(
        incident=incident,
        candidates=[payments_runbook],
        client=client,
    )

    assert selection == expected_selection

    request = client.responses.parse.call_args.kwargs
    assert request["text_format"] is AIRunbookSelection
    assert "payments-failure" in request["input"]


def test_runbook_recommendation_falls_back_when_ai_fails():
    incident = make_incident()
    payments_runbook = make_payments_runbook()

    client = Mock()
    client.responses.parse.side_effect = ValueError("AI unavailable")

    recommendation = recommend_runbook(
        incident=incident,
        runbooks=[payments_runbook],
        client=client,
    )

    assert recommendation.incident_id == incident.id
    assert recommendation.title == payments_runbook.title
    assert recommendation.content == payments_runbook.content
    assert recommendation.selection_method == "fallback"
    assert recommendation.confidence == "high"


def test_feature_flag_enables_ai_selection(monkeypatch):
    incident = make_incident()
    payments_runbook = make_payments_runbook()

    selection = AIRunbookSelection(
        runbook_id="payments-failure",
        confidence="high",
        reason="The retrieved runbook matches the incident.",
    )

    client = Mock()
    client.responses.parse.return_value.output_parsed = selection

    monkeypatch.setenv("RUNBOOK_AI_ENABLED", "true")
    monkeypatch.setattr(
        "app.ai_runbooks.load_runbooks",
        lambda _: [payments_runbook],
    )
    monkeypatch.setattr(
        "app.ai_runbooks.OpenAI",
        lambda: client,
    )

    recommendation = recommend_runbook_for_incident(incident)

    assert recommendation.selection_method == "ai"
    assert recommendation.title == payments_runbook.title
    assert recommendation.content == payments_runbook.content
    assert recommendation.confidence == "high"
    assert recommendation.reason == selection.reason


def test_ai_cannot_select_runbook_outside_retrieved_candidates():
    incident = make_incident()
    payments_runbook = make_payments_runbook()

    client = Mock()
    client.responses.parse.return_value.output_parsed = AIRunbookSelection(
        runbook_id="unretrieved-runbook",
        confidence="high",
        reason="Invalid selection.",
    )

    recommendation = recommend_runbook(
        incident=incident,
        runbooks=[payments_runbook],
        client=client,
    )

    assert recommendation.selection_method == "fallback"
    assert recommendation.title == payments_runbook.title
    assert recommendation.content == payments_runbook.content
