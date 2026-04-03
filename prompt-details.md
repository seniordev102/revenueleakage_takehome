You will implement this project in **phases**.
Do NOT build everything at once.
Wait for confirmation before moving to the next phase.

Follow strict architecture decisions already defined:

* Python + FastAPI backend
* React + TypeScript + Vite frontend
* DynamoDB single-table design
* S3 for uploads
* Hybrid AI agent (rule + LLM)
* Separate billing records and analysis results
* Unit tests for each module

---

# PHASE 1 — Project Setup & Structure

## Backend

Create a FastAPI project with:

* proper folder structure:

  * api/
  * services/
  * agents/
  * tools/
  * repositories/
  * schemas/
  * models/
  * core/
  * utils/

* install dependencies:

  * fastapi
  * uvicorn
  * pydantic
  * boto3
  * pytest
  * python-dotenv

* create:

  * main.py
  * basic health endpoint `/health`

## Frontend

Create Vite + React + TypeScript app with:

* Tailwind CSS
* React Query
* basic routing
* empty pages:

  * UploadPage
  * DashboardPage

## Output

* working backend server
* working frontend app
* README with setup steps

STOP after this phase.

---

# PHASE 2 — Core Data Models & Schemas

## Backend

Define Pydantic schemas:

* Upload
* BillingRecord
* AnalysisIssue
* AnalysisResult
* DashboardSummary

Define enums:

* Severity (HIGH, MEDIUM, LOW, INFO)
* IssueType

## Also implement:

* money utility functions
* base validation utilities

## Tests

* test schema validation
* test money calculations

STOP after this phase.

---

# PHASE 3 — File Ingestion

## Backend

Implement:

* CSV parser
* JSON parser
* upload endpoint

Flow:

1. upload file
2. validate file type
3. parse records
4. normalize records

## S3 integration

* upload raw file to S3
* return s3_key

## DynamoDB (basic)

* store upload metadata
* store billing records

## Tests

* CSV parsing
* JSON parsing
* normalization

STOP.

---

# PHASE 4 — DynamoDB Design Implementation

Implement:

* single-table design
* repository layer

Repositories:

* UploadRepository
* RecordRepository
* AnalysisRepository

Support:

* create upload item
* create billing record item
* update record summary fields
* create analysis item

## Tests

* item structure correctness
* repository mocks

STOP.

---

# PHASE 5 — Rule Engine (CRITICAL)

Implement tool modules:

* validation_tool
* pricing_tool
* quantity_tool
* discount_tool
* tax_tool
* duplicate_tool
* severity_tool

Each tool:

* pure function
* testable independently

## Tests (IMPORTANT)

Write unit tests for EACH:

* rate mismatch detection
* expected calculation
* discount logic
* tax logic
* severity assignment

STOP.

---

# PHASE 6 — AI Agent (Core)

Implement:

* LeakageAnalysisAgent

Flow:

1. validate record
2. run tools
3. aggregate issues
4. compute leakage
5. assign severity
6. decide if LLM needed
7. call Bedrock (mock first)
8. return structured output

## Important

* skip LLM if no issue
* structured JSON output only

## Tests

* agent orchestration
* LLM invocation decision logic

STOP.

---

# PHASE 7 — Bedrock Integration

Implement:

* Bedrock reasoning service

Prompt should:

* accept structured inputs
* return JSON only
* include reasoning + suggestion

## Add:

* mock fallback for tests

## Tests

* LLM response parsing
* fallback behavior

STOP.

---

# PHASE 8 — API Layer

Implement endpoints:

* POST /uploads
* GET /uploads
* GET /records
* GET /records/{id}
* GET /records/{id}/analysis
* GET /dashboard/summary

Support:

* filtering
* search
* sorting
* pagination

## Tests

* API responses
* filtering logic

STOP.

---

# PHASE 9 — Frontend Core

Implement:

## Upload Page

* file upload
* loading state
* success/error

## Dashboard Page

* summary cards
* severity filter
* records table

## Record Detail Drawer

* show issues
* reasoning
* suggestion

## Tests

* component rendering
* state behavior

STOP.

---

# PHASE 10 — Frontend Stretch Features

Add:

* search
* sorting
* pagination
* severity chart
* high-risk section

## Tests

* search behavior
* sorting
* pagination

STOP.

---

# PHASE 11 — Documentation

Generate:

* README.md
* docs/architecture.md
* docs/decision-reasons.md
* docs/api.md
* docs/testing.md
* docs/sample-data.md

Ensure:

* decisions match architecture
* DynamoDB reasoning included
* hybrid AI explanation included

STOP.

---

# PHASE 12 — Polish

Add:

* loading states
* error states
* empty states
* small UI improvements

Ensure:

* code readability
* consistent naming
* test coverage

END.
