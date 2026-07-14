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

## Run Tests

```bash
python -m pytest -v
```

## Project Status

This project is under active development. The persistent incident-management foundation is complete. Automated investigation, runbook retrieval, impact estimation, incident communications, postmortem generation, and the web interface are currently planned.