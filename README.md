# AI Agent Driven Revenue Leakage Detection Platform

This repository contains a take-home style project for an **AI Agent Driven Revenue Leakage Detection Platform**.

The system ingests pricing and billing datasets, detects revenue leakage with deterministic checks plus optional LLM reasoning, and surfaces results through a React dashboard.

## Stack

- **Backend**: Python, FastAPI, Pydantic, pytest
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Query, Vitest, React Testing Library
- **Persistence shape**: DynamoDB-style single-table repositories plus a runtime in-memory query store
- **AI integration**: OpenAI Chat Completions API for reasoning and suggestion enrichment
- **Operational design**: centralized settings, structured logging, dependency-injected services, and app-level error handling

Architecture and phased roadmap are defined in `prompt-details.md`, `prompt-simple.md`, and `cursor-prompt.md`.

Additional project documentation lives under `docs/`:

- `docs/architecture.md`
- `docs/api.md`
- `docs/testing.md`
- `docs/decision-reasons.md`
- `docs/sample-data.md`

---

## Backend (FastAPI)

Location: `backend/`

### Install

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run dev server

```bash
uvicorn app.main:app --reload --port 8000
```

### Configuration

The backend loads environment variables from `backend/.env` via `python-dotenv`.

Common settings:

- `APP_NAME`
- `APP_ENV`
- `LOG_LEVEL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_TIMEOUT_SECONDS`
- `OPENAI_BASE_URL`

If `OPENAI_API_KEY` is unset, the analysis pipeline still runs and falls back to deterministic reasoning text instead of calling the external API.

### Key endpoints

- **Health**: `GET /health` → `{ "status": "ok" }`
- **Uploads**: `POST /uploads`
  - Accepts `multipart/form-data` with a `file` field (CSV or JSON).
  - Returns upload metadata and a sample of enriched billing records.
- **Direct ingestion**: `POST /uploads/records`
  - Accepts a JSON array of billing records.
  - Useful for API-first tests and fixtures without multipart upload handling.
- **Records**:
  - `GET /records` with optional query params:
    - `upload_id`, `severity`, `flagged_only`, `search`, `page`, `page_size`
  - `GET /records/{record_id}`
- **Analysis**:
  - `GET /records/{record_id}/analysis` → list of analysis versions for a record.
  - Analysis incidents now return structured leakage details including:
    - `id`
    - `issue`
    - `expected_amount`
    - `billed_amount`
    - `leakage`
    - `reasoning`
    - `severity`
    - `suggestion`
- **Dashboard**:
  - `GET /dashboard/summary` → summary counts, total leakage, and a `data_source` field.
  - `GET /records` → paginated record list used by the dashboard table and chart.

### Tests

Backend tests live under `backend/app/tests/` and cover:

- money utilities and leakage rule
- schema validation
- CSV/JSON parsing and ingestion normalization
- DynamoDB item construction and repository behavior (with fakes)
- rule-engine tools (pricing, quantity, discount, tax, duplicates, severity)
- contract-term, tier-pricing, and manual-override anomaly checks
- AI agent orchestration and selective LLM invocation
- structured leakage incident generation and prioritization
- OpenAI service parsing and fallback
- basic API layer behavior
- service-layer ingestion and runtime-store query flow

Run all tests:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

---

## Frontend (React + Vite)

Location: `frontend/`

### Install

```bash
cd frontend
npm install
```

### Run dev server

```bash
npm run dev
```

By default Vite runs on `http://localhost:5173` (with the backend expected at `http://localhost:8000`).

### Current routes

- `/upload`
  - Tailwind-styled upload form using React Query.
  - Accepts CSV/JSON files and calls `POST /uploads`.
  - Shows loading state, success message with `upload_id` and processed record count, and error state.
- `/dashboard`
  - Uses React Query to call `GET /dashboard/summary`.
  - Uses React Query to call `GET /records` for the records table.
  - Renders summary cards for:
    - total records
    - flagged records
    - total leakage amount
    - high severity count
  - Each card supports loading and error states.
  - Renders a records table with:
    - expected amount, billed amount, leakage amount, and severity
    - pagination controls
    - severity filter wired to the records API
    - backend search across record, contract, customer, and product IDs
  - Renders a severity distribution chart for the currently visible records.
- `/records/:recordId`
  - Calls `GET /records/{record_id}/analysis`.
  - Shows analyzer metadata, total leakage, and incident-by-incident reasoning.

### Frontend tests

Frontend tests use Vitest + React Testing Library:

- `UploadPage.test.tsx` — verifies upload form renders and invokes the upload API, asserting success message.
- `DashboardPage.test.tsx` — verifies summary cards, severity filtering, search filtering, and severity chart rendering from mocked dashboard/records APIs.

Run tests:

```bash
cd frontend
npm test
```