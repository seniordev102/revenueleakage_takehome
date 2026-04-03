You are a senior full-stack AI/backend engineer. Build a take-home assessment project for an **AI Agent Driven Revenue Leakage Detection Platform**.

Your goal is to produce a clean, production-style, submission-ready project with strong architecture, clear documentation, solid unit tests, and a polished MVP + stretch feature set.

## Primary objective

Build a system that:

* uploads pricing/billing datasets in CSV or JSON
* stores raw uploads in S3
* stores processed records and analysis results in DynamoDB
* analyzes records for revenue leakage using a hybrid AI agent
* shows results in a React dashboard
* provides structured AI reasoning and corrective suggestions
* includes strong documentation, architecture explanation, and tests

## Locked technology decisions

Use exactly these choices unless absolutely necessary to adjust for implementation reality:

* Backend: **Python + FastAPI**
* Frontend: **React + TypeScript + Vite**
* Styling: **Tailwind CSS**
* Frontend data fetching: **React Query**
* Cloud: **AWS**
* Storage:

  * **S3** for raw uploaded files
  * **DynamoDB** for application data
* LLM: **AWS Bedrock**
* Testing:

  * Backend: **pytest**
  * Frontend: **Vitest + React Testing Library**

## Architecture decisions already made

These are intentional and must be reflected in code and documentation.

### Database choice

Use **DynamoDB** because:

* AWS-native architecture
* fast implementation for a 48-hour take-home
* schema flexibility for AI output
* good fit for scalable document-like analysis storage

### DynamoDB data model

Use a **single-table design** with separate entity types in the same table:

* upload metadata items
* billing/source record items
* analysis result items

Do **not** store analysis only inline on the source record.
Instead:

* keep raw/source billing records separate from generated AI analysis results
* support re-analysis/versioning
* denormalize small summary fields onto record items for fast dashboard rendering

Example intent:

* `UPLOAD` item
* `BILLING_RECORD` item
* `ANALYSIS_RESULT` item

### AI agent design

Use this exact design:

* **single orchestrator**
* **tool-based internal modules**
* **hybrid rule + LLM**
* **selective LLM invocation**
* **structured JSON output**

Meaning:

* deterministic rules perform calculations and leakage checks
* Bedrock is used for explanation, reasoning, suggestions, and ambiguous/missing-data cases
* Bedrock is **not** the primary calculator
* skip LLM calls for clean records unless needed

## Delivery expectation

Produce a submission-ready codebase with:

1. backend
2. frontend
3. README
4. architecture diagram or architecture markdown
5. sample dataset
6. API documentation
7. design explanation
8. unit tests for each small feature/module
9. decision-reasons document

---

# Functional requirements to implement

## Data ingestion

Support:

* CSV upload
* JSON upload
* REST API ingestion

Fields may include:

* contract_id
* customer_id
* product_id
* agreed_rate
* billed_rate
* quantity
* expected_amount
* billed_amount
* discount
* tax
* currency
* billing_date
* contract_start_date
* contract_end_date
* region

Allow schema extension where useful.

## Leakage detection scenarios

Implement at minimum:

* rate mismatch
* quantity mismatch
* expected vs billed difference
* incorrect discount
* currency mismatch
* duplicate entries
* negative pricing
* zero billing
* missing contract rate
* incorrect tax
* tier pricing mismatch
* out-of-contract billing

## Frontend UI requirements

Build a React UI that:

* uploads dataset
* displays processed records
* shows flagged leakage items
* displays AI reasoning
* filters by severity
* shows summary metrics

Also implement stretch UI features:

* one chart
* search
* sorting
* pagination
* dashboard can act as a lightweight risk dashboard
* high-risk records section

## Summary metrics

At minimum show:

* total records
* flagged records
* total leakage amount
* high severity count

---

# Required output behavior

## Structured AI output

Analysis output should support multiple issues per record and look conceptually like:

```json
{
  "record_id": "R-101",
  "issues": [
    {
      "issue_type": "RATE_MISMATCH",
      "severity": "HIGH",
      "expected_amount": 1000,
      "billed_amount": 920,
      "leakage_amount": 80,
      "reasoning": "The billed rate is lower than the agreed contract rate, causing underbilling.",
      "suggestion": "Update the billed rate and regenerate the invoice."
    }
  ],
  "has_leakage": true,
  "total_leakage_amount": 80,
  "analysis_status": "COMPLETED",
  "analyzer_type": "RULE_PLUS_LLM",
  "analysis_version": 1
}
```

## Severity logic

Implement deterministic severity rules, for example:

* High: large leakage or critical issue
* Medium: moderate leakage
* Low: small leakage
* Info: suspicious but non-loss anomaly

Define the thresholds clearly in code and documentation.

## Leakage rule

Use a clear default such as:

* `leakage_amount = max(expected_amount - billed_amount, 0)`

Document assumptions.

---

# Project structure

## Backend structure

Create a clean Python/FastAPI architecture similar to:

```text
backend/
  app/
    main.py
    api/
      routes/
        uploads.py
        records.py
        analysis.py
        dashboard.py
    core/
      config.py
      logging.py
    schemas/
      upload.py
      record.py
      analysis.py
      dashboard.py
    models/
      enums.py
    services/
      s3_service.py
      dynamodb_service.py
      ingestion_service.py
      record_service.py
      analysis_service.py
      bedrock_service.py
    agents/
      leakage_agent.py
    tools/
      validation_tool.py
      pricing_tool.py
      quantity_tool.py
      discount_tool.py
      tax_tool.py
      duplicate_tool.py
      severity_tool.py
      llm_reasoning_tool.py
    repositories/
      record_repository.py
      analysis_repository.py
      upload_repository.py
    utils/
      csv_parser.py
      json_parser.py
      money.py
```

## Frontend structure

Create a clean React/Vite app similar to:

```text
frontend/
  src/
    pages/
      UploadPage.tsx
      DashboardPage.tsx
    components/
      upload/
        FileUploadCard.tsx
      dashboard/
        SummaryCards.tsx
        SeverityFilter.tsx
        RecordsTable.tsx
        LeakageChart.tsx
        HighRiskSection.tsx
      records/
        RecordDetailDrawer.tsx
        IssueList.tsx
      common/
        Badge.tsx
        EmptyState.tsx
        LoadingSpinner.tsx
    services/
      api.ts
      uploads.ts
      records.ts
      dashboard.ts
    hooks/
      useUploads.ts
      useRecords.ts
      useDashboardSummary.ts
    types/
      upload.ts
      record.ts
      analysis.ts
    utils/
      formatCurrency.ts
      formatDate.ts
```

---

# API design

Implement clean REST endpoints such as:

* `POST /uploads`
* `GET /uploads`
* `GET /dashboard/summary`
* `GET /records`
* `GET /records/{record_id}`
* `GET /records/{record_id}/analysis`
* optional `POST /records/analyze` if useful internally

Support filtering:

* upload_id
* severity
* flagged_only
* search query
* sort field
* sort direction
* page
* page_size

---

# DynamoDB design requirements

Use one table, for example `RevenueLeakage`.

Implement separate item types.

## Upload metadata item

Stores:

* upload_id
* file_name
* file_type
* s3_key
* status
* uploaded_at
* record_count

## Billing record item

Stores:

* upload_id
* record_id
* source fields
* lightweight denormalized analysis summary fields:

  * has_leakage
  * severity
  * leakage_amount
  * issue_count
  * analysis_status

## Analysis result item

Stores:

* upload_id
* record_id
* analysis_version
* issues
* reasoning
* suggestion
* confidence_score
* analyzer_type
* created_at

Support future re-analysis with versions like:

* `ANALYSIS#record#v1`
* `ANALYSIS#record#v2`

Keep raw/source data separate from generated analysis.

---

# AI orchestration requirements

Implement a `LeakageAnalysisAgent` orchestrator.

It should:

1. validate the record
2. run deterministic tools/checks
3. aggregate findings
4. compute leakage
5. assign severity
6. decide whether LLM invocation is necessary
7. call Bedrock selectively
8. return structured JSON
9. persist analysis result
10. update summary fields on the record item

## Tool modules

Implement as separate small modules/services:

* validation tool
* pricing tool
* quantity tool
* discount tool
* tax tool
* duplicate tool
* severity tool
* llm reasoning tool

Keep them individually testable.

---

# Frontend requirements in more detail

## Upload page

* upload CSV/JSON
* show loading/success/error state
* show accepted formats
* show processed count if available

## Dashboard page

* summary cards
* severity filter
* search
* sorting
* pagination
* records table
* one chart
* high-risk records section

## Record detail drawer or modal

Show:

* raw/source billing fields
* issue list
* leakage amount
* severity
* AI reasoning
* corrective suggestion
* analysis metadata

---

# Stretch feature set

Include these stretch features, but keep the implementation realistic:

* severity distribution chart
* search by contract/customer/product
* sort by severity, leakage amount, billing date
* pagination
* confidence score in analysis output
* high-risk records section
* support multiple issues per record
* support analysis versioning in data model
* polished loading/empty/error states
* optional lightweight risk dashboard framing on the main dashboard

Do not overbuild with auth, microservices, or unnecessary real-time features.

---

# Testing requirements

This is extremely important.

Write **unit tests for each small feature/module**, not just a few broad tests.

## Backend tests must cover at minimum

* file validation
* CSV parsing
* JSON parsing
* normalization
* expected amount calculation
* rate mismatch detection
* quantity mismatch detection
* discount mismatch detection
* tax mismatch detection
* duplicate detection
* severity assignment
* selective LLM invocation decision
* DynamoDB item construction
* repository behavior with mocked AWS clients
* API schema validation
* agent orchestration logic

Use pytest and mocking where needed.

## Frontend tests must cover at minimum

* upload component rendering and validation
* summary cards rendering
* severity filter behavior
* records table rendering
* sorting behavior
* pagination behavior
* search behavior
* detail drawer rendering
* empty/loading/error states

Use Vitest + React Testing Library.

## Testing principle

Prefer many small focused tests over a few large brittle tests.

---

# Documentation requirements

Create the following files:

## 1. `README.md`

Must include:

* project overview
* architecture summary
* stack
* setup steps
* how to run backend
* how to run frontend
* how to run tests
* API summary
* assumptions/trade-offs

## 2. `docs/architecture.md`

Explain:

* system design
* ingestion flow
* analysis flow
* DynamoDB design
* S3 usage
* Bedrock role
* why hybrid rule + LLM was chosen
* scalability considerations

## 3. `docs/decision-reasons.md`

This file is mandatory.
Write down the reasons behind the major choices already made.

Include at minimum:

### Why DynamoDB

* AWS-native architecture
* fast implementation
* schema flexibility for AI output

### Why single-table with separate analysis items

* separates raw billing data from generated AI output
* supports re-analysis/versioning
* enables denormalized summary fields for fast UI rendering

### Why Python + FastAPI

* strong fit for AI/data/backend workflows
* fast structured API development
* good typing/validation with Pydantic

### Why hybrid AI agent

* deterministic rules are more reliable for billing calculations
* LLM is better for explanations/suggestions
* selective LLM invocation reduces cost/latency
* stronger production-grade architecture

### Why React + Vite frontend

* lightweight dashboard delivery
* fast implementation
* enough to satisfy required UI and stretch features

Also include key assumptions and trade-offs.

## 4. `docs/api.md`

Document major endpoints and response shapes.

## 5. `docs/testing.md`

Explain:

* backend test strategy
* frontend test strategy
* mocking strategy for AWS/Bedrock
* where unit tests exist

## 6. `docs/sample-data.md`

Explain the sample dataset fields and sample anomalies included.

---

# Quality bar

The project should feel:

* senior-level
* modular
* readable
* maintainable
* not over-engineered
* realistic for a take-home

Use clean naming, small focused modules, and consistent types.

Prefer simple, correct, testable code over flashy complexity.

---

# Implementation guidance

## Backend implementation style

* use Pydantic models heavily
* keep route handlers thin
* place business logic in services/agent/tools
* isolate AWS calls in service/repository layers
* mock Bedrock and AWS in tests
* keep deterministic rules explicit and inspectable

## Frontend implementation style

* use typed API clients
* use React Query for server state
* keep components small and focused
* keep styling clean and dashboard-oriented
* use a detail drawer/modal rather than a separate heavy page if simpler

---

# Final output expectation

Generate a complete codebase and documentation for this take-home assessment.

The result should be something a senior engineer would reasonably submit, with:

* working backend
* working frontend
* credible architecture
* strong reasoning
* clear docs
* strong unit test coverage for each small feature/module

When making decisions, preserve the locked architecture choices above rather than replacing them with easier alternatives.
