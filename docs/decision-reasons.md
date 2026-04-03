# Decision Reasons

## Why a Hybrid Rule + LLM Approach

The project uses deterministic checks first and optional LLM reasoning second.

Reasons:

- pricing, quantity, discount, and tax mismatches are easier to verify with explicit rules
- deterministic checks provide repeatable leakage amounts and severities
- the LLM is better suited to explanation, corrective guidance, and ambiguity handling than primary arithmetic
- this split reduces hallucination risk and keeps financial calculations auditable

## Why Structured Leakage Incidents

Analysis incidents now include fields such as:

- `id`
- `issue`
- `expected_amount`
- `billed_amount`
- `leakage`
- `reasoning`
- `severity`
- `suggestion`

Reasons:

- the UI and downstream consumers need something more useful than a plain message string
- structured incidents make prioritization and remediation easier
- the same shape can be enriched by LLM output without changing the overall contract

## Why Use a Runtime Store for Queries

The read-side APIs currently serve records, analysis results, and dashboard aggregates from `RuntimeStore`.

Reasons:

- local development remains simple and fast
- the frontend gets immediate read-after-write behavior without external setup
- query behavior can evolve independently from the persistence schema

Trade-off:

- query state is process-local and transient

## Why Keep DynamoDB-Style Repositories Anyway

Repository classes are already present for uploads, records, and analysis results, and writes flow through them today.

Reasons:

- the intended target architecture is a single-table DynamoDB design
- key structure and access patterns can be validated early
- it reduces future rewrite cost when moving from runtime-store reads to persistent query flows

## Why the Dashboard Uses Backend Filtering

The dashboard currently uses:

- backend filtering for severity
- backend search for record, contract, customer, and product text

Reasons:

- severity already exists as an API query parameter
- keeping search on the backend makes dashboard behavior match API consumers and tests
- it avoids splitting filtering logic between the server and UI

Trade-off:

- search still only sees the data present in the runtime store for the current process

## Why Add a Direct JSON Ingestion Endpoint

The backend exposes both `POST /uploads` and `POST /uploads/records`.

Reasons:

- browser flows still need multipart file upload support
- tests and API-first consumers benefit from sending JSON directly
- both entrypoints can share the same normalization and processing pipeline

## Why the Severity Chart Is Custom

The dashboard uses a simple custom bar chart instead of a charting library.

Reasons:

- it avoids adding an extra dependency for a small visualization
- it is easy to style consistently with the rest of the Tailwind UI
- it keeps the chart testable through accessible labels and predictable markup

## Why Duplicate Checks Are Separated

Duplicate detection is implemented as a batch-oriented tool instead of a per-record rule.

Reason:

- duplicate detection naturally compares records against one another rather than evaluating one row in isolation

Current implication:

- duplicate logic exists and is tested, but it is merged after per-record analysis rather than inside the single-record tool pass

## Why Use Structured Error Responses

Application-specific failures use an `{ "error": { "code", "message" } }` envelope.

Reasons:

- clients can distinguish validation and domain failures from generic HTTP status text
- tests can assert stable error codes
- the format scales better as the API surface grows

## Why the Current Scope Stops Here

The repository intentionally prioritizes:

- clear domain models
- testable business logic
- a working upload and dashboard loop
- future-compatible persistence and reasoning layers

This keeps the implementation compact while leaving a clear path for:

- repository-backed read models
- richer querying and historical analysis views
- detailed analysis views in the frontend
