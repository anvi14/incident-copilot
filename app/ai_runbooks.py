import json
import os
from pathlib import Path
from typing import Literal

from openai import OpenAI, OpenAIError
from pydantic import BaseModel

from app.models import Incident, RunbookRecommendation
from app.runbooks import (
    Runbook,
    find_runbook,
    load_runbooks,
    retrieve_runbooks,
)

RUNBOOKS_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "runbooks"
)


class AIRunbookSelection(BaseModel):
    runbook_id: str
    confidence: Literal["low", "medium", "high"]
    reason: str


def select_runbook_with_ai(
    incident: Incident,
    candidates: list[Runbook],
    client: OpenAI,
) -> AIRunbookSelection:
    candidate_data = [
        {
            "id": candidate.id,
            "title": candidate.title,
            "content": candidate.content,
        }
        for candidate in candidates
    ]

    prompt = (
        "Incident:\n"
        f"{incident.model_dump_json(indent=2)}\n\n"
        "Retrieved approved runbooks:\n"
        f"{json.dumps(candidate_data, indent=2)}"
    )

    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        instructions=(
            "Select the best runbook from the retrieved candidates. "
            "Select only a supplied runbook ID. Do not invent or "
            "modify operational content."
        ),
        input=prompt,
        text_format=AIRunbookSelection,
    )

    if response.output_parsed is None:
        raise ValueError("The model did not return a runbook selection")

    return response.output_parsed


def recommend_runbook(
    incident: Incident,
    runbooks: list[Runbook],
    client: OpenAI,
) -> RunbookRecommendation:
    candidates = retrieve_runbooks(incident, runbooks)

    if not candidates:
        raise ValueError("No matching or fallback runbook found")

    try:
        selection = select_runbook_with_ai(
            incident=incident,
            candidates=candidates,
            client=client,
        )
        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate.id == selection.runbook_id
            ),
            None,
        )

        if selected is None:
            raise ValueError(
                "AI selected a runbook outside the retrieved candidates"
            )
    except (OpenAIError, ValueError):
        return find_runbook(incident, runbooks)

    return RunbookRecommendation(
        incident_id=incident.id,
        title=selected.title,
        steps=[],
        content=selected.content,
        selection_method="ai",
        confidence=selection.confidence,
        reason=selection.reason,
    )


def recommend_runbook_for_incident(
    incident: Incident,
) -> RunbookRecommendation:
    runbooks = load_runbooks(RUNBOOKS_DIRECTORY)

    ai_enabled = (
        os.getenv("RUNBOOK_AI_ENABLED", "false").lower()
        == "true"
    )

    if not ai_enabled:
        return find_runbook(incident, runbooks)

    try:
        client = OpenAI()
    except OpenAIError:
        return find_runbook(incident, runbooks)

    return recommend_runbook(
        incident=incident,
        runbooks=runbooks,
        client=client,
    )
