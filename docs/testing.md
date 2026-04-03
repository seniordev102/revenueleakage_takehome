# Testing

## Overview

The repository includes automated tests for both backend and frontend behavior.

- backend tests use `pytest`
- frontend tests use `Vitest` and `React Testing Library`

## Backend Test Location

Backend tests live in `backend/app/tests/`.

Current test modules include:

- `test_api_layer.py`
- `test_dynamodb_deserialize.py`
- `test_openai_service.py`
- `test_ingestion_service.py`
- `test_leakage_agent.py`
- `test_money.py`
- `test_parsers.py`
- `test_repositories.py`
- `test_schemas.py`
- `test_tools_pricing_and_severity.py`
- `test_tools_quantity_discount_tax_duplicate.py`
- `test_validation.py`

## Backend Coverage Areas

The backend suite covers:

- money calculations and leakage helpers
- schema validation and serialization
- CSV and JSON parsing
- ingestion normalization and generated IDs
- structured application errors and API-level validation
- deterministic rule tools:
  - pricing
  - quantity
  - discount
  - tax
  - contract term and tier pricing
  - duplicates
  - manual override
  - severity assignment
- repository item construction for the DynamoDB single-table model
- query-service behavior over the runtime store
- OpenAI service parsing and fallback behavior
- leakage agent orchestration and LLM enrichment behavior
- API endpoint behavior including backend search and JSON-body ingestion

## Backend Test Commands

Run all backend tests:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Run a focused subset:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
pytest app/tests/test_leakage_agent.py app/tests/test_openai_service.py
```

## Frontend Test Location

Frontend page tests live under `frontend/src/pages/`.

Current test files:

- `UploadPage.test.tsx`
- `DashboardPage.test.tsx`

## Frontend Coverage Areas

The frontend suite currently verifies:

- upload form rendering and upload API invocation
- dashboard summary card rendering from mocked API responses
- severity filter wiring in the dashboard records query
- backend search parameter wiring in the dashboard records query
- severity chart rendering from loaded records

## Frontend Test Commands

Run all frontend tests:

```bash
cd frontend
npm test
```

Run the dashboard tests once:

```bash
cd frontend
npm test -- DashboardPage.test.tsx --run
```

## Testing Strategy

The current testing approach is intentionally lightweight:

- backend logic is tested heavily at the unit, service, and repository-adapter levels
- API behavior is verified with focused route tests against the FastAPI app
- frontend behavior is tested through page-level interactions with mocked API calls

This keeps feedback fast while covering the highest-risk logic paths.

## Known Gaps

Current testing gaps include:

- no end-to-end browser tests across upload through dashboard flows
- no external-infrastructure integration tests beyond the in-memory DynamoDB client
- no frontend tests yet for `RecordAnalysisPage`
