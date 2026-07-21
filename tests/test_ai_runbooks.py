from unittest.mock import Mock

from app.ai_runbooks import (
    AIRunbookSelection,
    recommend_runbook,
    recommend_runbook_for_incident,
    select_runbook_with_ai,
)
from app.models import Incident


def test_ai_selects_approved_runbook():
    incident = Incident(
        id=1,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing",
        status="open",
        suspected_category="payments",
    )

    expected_selection = AIRunbookSelection(
        runbook_id="payments",
        confidence="high",
        reason="The payments runbook directly matches the failure symptoms.",
    )

    client = Mock()
    client.responses.parse.return_value.output_parsed = expected_selection

    selection = select_runbook_with_ai(
        incident=incident,
        client=client,
    )

    assert selection == expected_selection
    assert selection.runbook_id == "payments"

    client.responses.parse.assert_called_once()
    request = client.responses.parse.call_args.kwargs
    assert request["text_format"] is AIRunbookSelection
    assert "Payments Failure Runbook" in request["input"]


def test_runbook_recommendation_falls_back_when_ai_fails():
    incident = Incident(
        id=1,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing",
        status="open",
        suspected_category="payments",
    )

    client = Mock()
    client.responses.parse.side_effect = ValueError("AI unavailable")

    recommendation = recommend_runbook(
        incident=incident,
        client=client,
    )

    assert recommendation.incident_id == incident.id
    assert recommendation.title == "Payments Failure Runbook"
    assert recommendation.selection_method == "fallback"
    assert recommendation.confidence == "high"
    assert "category" in recommendation.reason.lower()


def test_feature_flag_enables_ai_selection(monkeypatch):
    incident = Incident(
        id=1,
        service="payments-api",
        severity="critical",
        message="Payment requests are failing",
        status="open",
        suspected_category="payments",
    )

    selection = AIRunbookSelection(
        runbook_id="payments",
        confidence="high",
        reason="The incident directly matches the payments runbook.",
    )

    client = Mock()
    client.responses.parse.return_value.output_parsed = selection

    monkeypatch.setenv("RUNBOOK_AI_ENABLED", "true")
    monkeypatch.setattr(
        "app.ai_runbooks.OpenAI",
        lambda: client,
    )

    recommendation = recommend_runbook_for_incident(incident)

    assert recommendation.selection_method == "ai"
    assert recommendation.title == "Payments Failure Runbook"
    assert recommendation.confidence == "high"
    assert recommendation.reason == selection.reason
