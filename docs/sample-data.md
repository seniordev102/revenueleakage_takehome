# Sample Data

## Location

Bundled sample files live in `sample_data/`.

Current files:

- `sample_data/sample_billing.json`
- `sample_data/record_explain.md`

## Purpose

The sample dataset provides a compact set of billing scenarios for:

- upload and parsing demos
- dashboard exploration
- leakage rule validation
- explaining expected anomaly coverage

## Record Format

The JSON file contains an array of normalized-ish billing records with fields such as:

- `contract_id`
- `customer_id`
- `product_id`
- `agreed_rate`
- `billed_rate`
- `quantity`
- `expected_amount`
- `billed_amount`
- `discount`
- `tax`
- `currency`
- `billing_date`
- `contract_start_date`
- `contract_end_date`
- `region`

Some records include scenario-specific fields such as:

- `tier_pricing`
- `manual_override`

## Included Scenarios

The companion `record_explain.md` file maps the sample contracts to their intended scenarios:

- `C-001` - rate mismatch
- `C-002` - expected vs billed difference
- `C-003` - discount mismatch
- `C-004` - tax mismatch
- `C-005` - duplicate entry scenario
- `C-006` - negative pricing
- `C-007` - zero billing or missing charge
- `C-008` - missing contract rate
- `C-009` - out-of-contract billing
- `C-010` - tier pricing mismatch
- `C-011` - clean record

## How the Sample Data Is Used Today

Current behavior:

- the upload endpoint can ingest the sample JSON directly
- the JSON-body ingestion endpoint can ingest equivalent records directly
- ingestion normalizes records and adds generated IDs
- processing enriches each record with leakage and severity summary fields
- the dashboard can then display the uploaded records, apply backend filtering and search, and show the severity distribution chart
- the record analysis page can display the latest stored analysis result for a selected record

## Known Mismatch Between Sample Scope and Implemented Rules

The sample data still covers a slightly broader roadmap than the currently active query and UI surfaces.

Implemented today:

- rate mismatch
- expected vs billed difference
- discount mismatch
- tax mismatch
- duplicate detection
- negative pricing
- zero billing
- missing required-field style validation
- out-of-contract billing
- tier pricing mismatch
- manual override errors

Still worth noting:

- duplicate detection is batch-oriented and merged after per-record analysis
- broader currency conversion mistakes are still beyond the current simple currency mismatch logic

## Suggested Usage

For manual validation during development:

1. Start the backend and frontend locally.
2. Upload `sample_data/sample_billing.json`.
3. Open the dashboard and inspect:
   - summary cards
   - severity filter behavior
   - table search behavior
   - severity chart distribution
4. Use `sample_data/record_explain.md` as the quick reference for what each sample contract is meant to demonstrate.
