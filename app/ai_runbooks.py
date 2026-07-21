import json
import os
from typing import Literal

from openai import OpenAI, OpenAIError
from pydantic import BaseModel

from app.models import Incident, RunbookRecommendation
from app.runbooks import RUNBOOKS, find_runbook


class AIRunbookSelection(BaseModel):
    runbook_id: Literal[
        "payments",
        "performance",
        "database",
        "unknown",
    ]
    confidence: Literal["low", "medium", "high"]
    reason: str


def select_runbook_with_ai(
    incident: Incident,
    client: OpenAI,
) -> AIRunbookSelection:
    prompt = (
        "Incident:\n"
        f"{incident.model_dump_json(indent=2)}\n\n"
        "Approved runbooks:\n"
        f"{json.dumps(RUNBOOKS, indent=2)}"
    )

    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        instructions=(
            "Select the single approved runbook that best matches "
            "the incident. Select only a supplied runbook ID. "
            "Do not invent or modify operational steps."
        ),
        input=prompt,
        text_format=AIRunbookSelection,
    )

    if response.output_parsed is None:
        raise ValueError("The model did not return a runbook selection")

    return response.output_parsed


def recommend_runbook(
    incident: Incident,
    client: OpenAI,
) -> RunbookRecommendation:
    try:
        selection = select_runbook_with_ai(
            incident=incident,
            client=client,
        )
    except (OpenAIError, ValueError):
        return find_runbook(incident)

    runbook = RUNBOOKS[selection.runbook_id]

    return RunbookRecommendation(
        incident_id=incident.id,
        title=runbook["title"],
        steps=runbook["steps"],
        selection_method="ai",
        confidence=selection.confidence,
        reason=selection.reason,
    )


def recommend_runbook_for_incident(
    incident: Incident,
) -> RunbookRecommendation:
    ai_enabled = (
        os.getenv("RUNBOOK_AI_ENABLED", "false").lower()
        == "true"
    )

    if not ai_enabled:
        return find_runbook(incident)

    try:
        client = OpenAI()
    except OpenAIError:
        return find_runbook(incident)

    return recommend_runbook(
        incident=incident,
        client=client,
    )
