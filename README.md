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
- Load approved operational runbooks from local Markdown files
- Rank runbooks using service, category, severity, and message text
- Return the original approved Markdown content without generating new steps
- Use an approved general-triage runbook when nothing relevant matches
- Optionally use OpenAI only to rerank locally retrieved candidates
- Work without an OpenAI API key using deterministic local retrieval

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
- OpenAI Python SDK for optional runbook reranking

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check API availability |
| `POST` | `/alerts` | Create an incident from an alert |
| `GET` | `/incidents` | List incidents |
| `GET` | `/incidents/{incident_id}` | Retrieve an incident |
| `PATCH` | `/incidents/{incident_id}/status` | Update incident status |
| `GET` | `/incidents/{incident_id}/runbook` | Retrieve the most relevant approved runbook |

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

## Local Runbook Retrieval

Approved runbooks are stored in the `runbooks/` directory as Markdown files with metadata describing relevant services, incident categories, and severities.

For each incident, the application:

1. Loads the approved Markdown runbooks.
2. Scores them using service, category, severity, and message overlap.
3. Returns the highest-ranked approved runbook.
4. Uses the approved general-triage runbook when nothing matches.

The API returns the original Markdown body. It does not generate or rewrite operational steps.

## Optional AI Reranking

OpenAI integration is disabled by default. Without an API key, the application uses deterministic local retrieval.

When enabled, OpenAI may select only from the candidates returned by local retrieval. The selected runbook’s original approved content is returned unchanged. If AI selection fails or returns an invalid candidate, the application falls back to deterministic retrieval.

To enable AI reranking:

```bash
export RUNBOOK_AI_ENABLED=true
export OPENAI_API_KEY="your-api-key"
```

You can optionally configure the model:

```bash
export OPENAI_MODEL="your-model"
```

## Run Tests

```bash
python -m pytest -v
```

## Project Status

Incident Copilot currently supports persistent incident management, timeline auditing, simulated commit investigation, local retrieval of approved Markdown runbooks, deterministic fallback, and optional AI reranking of retrieved candidates.

Customer-impact estimation, incident communications, postmortem generation, and the web interface are planned next.
