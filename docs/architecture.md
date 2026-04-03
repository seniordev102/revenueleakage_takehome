# Architecture

## Overview

The project is a two-part application:

- a FastAPI backend that ingests billing files, normalizes records, computes leakage indicators, and exposes APIs
- a React frontend that uploads files and visualizes dashboard summaries and record-level results

The repository combines a service-oriented FastAPI runtime, a lightweight in-memory query store for interactive reads, DynamoDB-style repository classes for persistence writes, and an OpenAI reasoning wrapper for optional enrichment.

## Backend Structure

Key backend areas:

- `backend/app/main.py` wires the FastAPI application, logging, settings, routers, and exception handlers
- `backend/app/api/` contains HTTP endpoints for uploads, records, analysis, and dashboard summary
- `backend/app/dependencies.py` constructs the app's cached services, repositories, agent, and runtime store
- `backend/app/services/ingestion_service.py` parses raw files or JSON bodies and normalizes records
- `backend/app/services/processing_service.py` persists uploads and records, runs analysis, and hydrates runtime query state
- `backend/app/services/*_query_service.py` serve read-side queries for records, analysis, and dashboard data
- `backend/app/tools/` contains deterministic leakage checks such as pricing, quantity, discount, tax, contract, manual override, validation, and duplicate detection
- `backend/app/agents/leakage_agent.py` orchestrates rule-based checks and optional LLM enrichment
- `backend/app/repositories/` contains DynamoDB-oriented persistence logic for uploads, records, and analysis results
- `backend/app/stores/runtime_store.py` is the in-memory read model used by the query services
- `backend/app/schemas/common.py` defines the shared Pydantic models used across the backend

## Frontend Structure

Key frontend areas:

- `frontend/src/pages/UploadPage.tsx` handles file upload and status feedback
- `frontend/src/pages/DashboardPage.tsx` renders summary cards, records table, filters, pagination, and severity chart
- `frontend/src/pages/RecordAnalysisPage.tsx` renders the latest analysis result and incident details for a selected record
- `frontend/src/services/api.ts` contains the frontend fetch wrappers for backend endpoints

## Data Flow

### Upload flow

1. A user uploads a CSV or JSON file through the frontend, or sends normalized records directly to `POST /uploads/records`.
2. The route passes bytes or records into `IngestionService`.
3. The ingestion service parses CSV or JSON when needed and normalizes records:
   - generates `upload_id`
   - assigns deterministic `record_id` values such as `r_0001`
   - computes `expected_amount` when it can be derived from `agreed_rate * quantity`
4. `ProcessingService` writes upload and record items through repository interfaces backed by `DynamoDBService`.
5. `ProcessingService` runs duplicate detection across the batch, calls `LeakageAnalysisAgent` for each record, and stores:
   - enriched records in `RuntimeStore`
   - analysis results in `RuntimeStore`
   - analysis items and record summary-field updates through the repository layer
6. The upload route returns upload metadata, record count, and a three-record sample.

### Analysis flow

1. A `BillingRecord` is passed to `LeakageAnalysisAgent`.
2. The agent runs deterministic checks from the tools layer:
   - validation
   - pricing
   - quantity
   - discount
   - tax
   - contract term and tier pricing
   - manual override
3. Each check returns structured leakage incidents with fields such as:
   - `id`
   - `issue`
   - `expected_amount`
   - `billed_amount`
   - `leakage`
   - `reasoning`
   - `severity`
   - `suggestion`
4. The agent totals leakage and prioritizes incidents by severity and leakage amount.
5. Batch duplicate detection is merged into each record's result after single-record analysis.
6. If the record has leakage and rule-based findings, the OpenAI wrapper can enrich reasoning and suggestions.
7. The repository layer persists:
   - analysis results as `ANALYSIS_RESULT` items
   - record summary fields such as severity, issue count, and total leakage

### Dashboard flow

1. The frontend requests `GET /dashboard/summary` for top-level metrics.
2. The frontend requests `GET /records` for paginated record rows.
3. The dashboard page applies:
   - backend severity filtering through the `severity` query parameter
   - backend free-text search through the `search` query parameter
4. The records table and severity chart both reflect the current visible records.
5. The user can navigate to `/records/:recordId` to inspect the latest stored analysis result for that record.

## Current Runtime Model

There are two layers to be aware of:

- writes go through repository classes and `DynamoDBService`
- reads for `GET /records`, `GET /records/{record_id}/analysis`, and `GET /dashboard/summary` come from `RuntimeStore`

In local development and tests, `DynamoDBService` is backed by the in-memory `runtime_dynamo_client`, so the repository layer is exercised without requiring external infrastructure.

## Storage Model

The repository layer follows a single-table DynamoDB design:

- upload metadata uses `pk=UPLOAD#{upload_id}` and `sk=META`
- billing records use `pk=UPLOAD#{upload_id}` and `sk=RECORD#{record_id}`
- analysis results use `pk=UPLOAD#{upload_id}` and `sk=ANALYSIS#{record_id}#v{version}`

Additional GSIs are prepared in record items for severity- and flagged-oriented access patterns.

## Limitations

Current limitations worth noting:

- the query side still relies on transient process memory rather than repository-backed reads
- frontend API configuration is still hard-coded to `http://localhost:8000`
- duplicate detection is batch-oriented and merged after per-record analysis instead of being part of the single-record tool pass
- no full end-to-end browser or external-infrastructure integration coverage is included yet
