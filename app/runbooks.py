import re
from pathlib import Path

from pydantic import BaseModel

from app.models import Incident, RunbookRecommendation


class Runbook(BaseModel):
    id: str
    title: str
    services: list[str]
    categories: list[str]
    severities: list[str]
    content: str
    is_fallback: bool = False


def parse_front_matter(lines: list[str]) -> dict[str, str | list[str]]:
    metadata: dict[str, str | list[str]] = {}
    current_list: str | None = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("- "):
            if current_list is None:
                raise ValueError("List item found without a metadata field")

            value = stripped.removeprefix("- ").strip()
            field = metadata[current_list]

            if not isinstance(field, list):
                raise ValueError(f"{current_list} is not a list")

            field.append(value)
            continue

        key, separator, value = stripped.partition(":")

        if not separator:
            raise ValueError(f"Invalid metadata line: {stripped}")

        key = key.strip()
        value = value.strip()

        if value:
            metadata[key] = value
            current_list = None
        else:
            metadata[key] = []
            current_list = key

    return metadata


def load_runbooks(directory: Path) -> list[Runbook]:
    runbooks = []

    for path in sorted(directory.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

        if not lines or lines[0].strip() != "---":
            raise ValueError(f"{path.name} is missing front matter")

        try:
            closing_delimiter = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as error:
            raise ValueError(
                f"{path.name} has unclosed front matter"
            ) from error

        metadata = parse_front_matter(lines[1:closing_delimiter])
        content = "".join(lines[closing_delimiter + 1:])

        runbooks.append(
            Runbook(
                id=metadata["id"],
                title=metadata["title"],
                services=metadata["services"],
                categories=metadata["categories"],
                severities=metadata["severities"],
                content=content,
                is_fallback=metadata.get("is_fallback") == "true",
            )
        )

    return runbooks


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_runbook(incident: Incident, runbook: Runbook) -> int:
    score = 0

    services = {service.lower() for service in runbook.services}
    categories = {category.lower() for category in runbook.categories}
    severities = {severity.lower() for severity in runbook.severities}

    if incident.service.lower() in services:
        score += 8

    if incident.suspected_category.lower() in categories:
        score += 4

    if incident.severity.lower() in severities:
        score += 2

    incident_terms = tokenize(incident.message)
    runbook_terms = tokenize(f"{runbook.title} {runbook.content}")
    score += len(incident_terms & runbook_terms)

    return score


def retrieve_runbooks(
    incident: Incident,
    runbooks: list[Runbook],
) -> list[Runbook]:
    fallback = next(
        (runbook for runbook in runbooks if runbook.is_fallback),
        None,
    )

    scored_runbooks = [
        (score_runbook(incident, runbook), runbook)
        for runbook in runbooks
        if not runbook.is_fallback
    ]

    matches = [
        runbook
        for score, runbook in sorted(
            scored_runbooks,
            key=lambda item: item[0],
            reverse=True,
        )
        if score > 0
    ]

    if matches:
        return matches

    return [fallback] if fallback else []


def find_runbook(
    incident: Incident,
    runbooks: list[Runbook],
) -> RunbookRecommendation:
    matches = retrieve_runbooks(incident, runbooks)

    if not matches:
        raise ValueError("No matching or fallback runbook found")

    runbook = matches[0]

    return RunbookRecommendation(
        incident_id=incident.id,
        title=runbook.title,
        steps=[],
        content=runbook.content,
        selection_method="fallback",
        confidence="low" if runbook.is_fallback else "high",
        reason=(
            "Selected from approved Markdown runbooks using "
            "local retrieval."
        ),
    )
