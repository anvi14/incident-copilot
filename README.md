# Incident Copilot

Incident Copilot is an AI-assisted incident response platform designed to help engineering teams investigate and respond to production outages.

The completed system will ingest alerts, identify likely problematic commits, retrieve relevant runbooks, estimate user impact, draft incident updates, and generate postmortems.

## Current Features

- Receive production alerts through a FastAPI endpoint
- Create and persist incidents in SQLite
- Categorize incidents using initial rule-based detection
- List incidents and retrieve individual incidents
- Track incidents through an operational lifecycle:
  - `open`
  - `investigating`
  - `mitigated`
  - `resolved`
- Validate API behavior with isolated automated tests
- Record alert ingestion, status changes, investigation findings, and runbook recommendations in an incident timeline
- Identify a suspected commit using deterministic simulated investigation data
- Recommend approved runbooks with confidence and reasoning
- Optionally use OpenAI structured outputs to select an approved runbook
- Fall back to deterministic category matching when AI is disabled or unavailable

## Planned Incident Workflow

```text
Alert fires
    ↓
Incident created
    ↓
Likely bad commit identified
    ↓
Relevant runbook retrieved
    ↓
Customer impact estimated
    ↓
Incident update generated
    ↓
Resolution tracked
    ↓
Postmortem generated
```

## Technology Stack

- Python
- FastAPI
- Pydantic
- SQLite
- pytest
- OpenAI Python SDK for optional structured runbook selection

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check API availability |
| `POST` | `/alerts` | Create an incident from an alert |
| `GET` | `/incidents` | List incidents |
| `GET` | `/incidents/{incident_id}` | Retrieve an incident |
| `PATCH` | `/incidents/{incident_id}/status` | Update incident status |

## Run Locally

Clone the repository and enter the project directory:

```bash
git clone https://github.com/anvi14/incident-copilot.git
cd incident-copilot
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Optional AI Runbook Selection

AI runbook selection is disabled by default. Without configuration, the application uses deterministic category-based matching.

To enable the optional OpenAI selector:

```bash
export RUNBOOK_AI_ENABLED=true
export OPENAI_API_KEY="your-api-key"

## Run Tests

```bash
python -m pytest -v
```
```markdown
## Project Status

Incident Copilot currently supports persistent incident management, timeline auditing, simulated commit investigation, approved runbook recommendations, and optional AI-assisted runbook selection with deterministic fallback.

Local Markdown retrieval, customer-impact estimation, incident communications, postmortem generation, and the web interface are planned next.