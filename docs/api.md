# API Documentation

## Base URL

Local development defaults:

- backend: `http://localhost:8000`
- frontend: `http://localhost:5173`

## Error Envelope

Application-defined errors are returned as:

```json
{
  "error": {
    "code": "INGESTION_ERROR",
    "message": "Unsupported file type. Use CSV or JSON."
  }
}
```

## Health

### `GET /health`

Returns a simple health response.

Example response:

```json
{ "status": "ok" }
```

## Uploads

### `POST /uploads`

Accepts a billing file upload as `multipart/form-data`.

Supported content types:

- `text/csv`
- `application/json`

Behavior:

- parses the uploaded file
- normalizes records
- assigns `upload_id` and `record_id`
- persists upload, record, and analysis items through the repository layer
- computes `has_leakage`, `leakage_amount`, and `severity`
- hydrates the runtime query store used by the read APIs

Example response shape:

```json
{
  "upload": {
    "upload_id": "u_ab12cd34",
    "file_name": "sample_billing.json",
    "file_type": "json",
    "s3_key": null,
    "status": "INGESTED",
    "uploaded_at": "2026-04-02",
    "record_count": 12
  },
  "record_count": 12,
  "sample_records": [
    {
      "upload_id": "u_ab12cd34",
      "record_id": "r_0001",
      "contract_id": "C-001",
      "customer_id": "CU-100",
      "product_id": "P-101",
      "expected_amount": 1000,
      "billed_amount": 920,
      "has_leakage": true,
      "leakage_amount": 80,
      "severity": "LOW"
    }
  ]
}
```

Error behavior:

- returns `400` for unsupported file types
- returns `400` if parsing fails or the payload is malformed

### `POST /uploads/records`

Accepts a JSON array of `BillingRecord`-shaped objects and runs the same normalization, persistence, analysis, and runtime-store hydration flow as `POST /uploads`.

Example request body:

```json
[
  {
    "contract_id": "C-API-001",
    "customer_id": "CU-API-100",
    "product_id": "P-API-ALPHA",
    "agreed_rate": 100,
    "billed_rate": 90,
    "quantity": 10,
    "expected_amount": 1000,
    "billed_amount": 900,
    "discount": 0,
    "tax": 0,
    "currency": "USD",
    "billing_date": "2026-03-25",
    "contract_start_date": "2026-01-01",
    "contract_end_date": "2026-12-31",
    "region": "US"
  }
]
```

Notes:

- an empty array returns `400`
- the generated upload uses `file_type: "api"`

## Records

### `GET /records`

Returns paginated records from the runtime query store.

Supported query parameters:

- `upload_id`
- `severity`
- `flagged_only`
- `search`
- `page`
- `page_size`

Example:

`GET /records?severity=HIGH&search=alpha&page=1&page_size=10`

Example response shape:

```json
{
  "total": 3,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "record_id": "r_0001",
      "contract_id": "C-001",
      "customer_id": "CU-100",
      "product_id": "P-101",
      "expected_amount": 1000,
      "billed_amount": 920,
      "leakage_amount": 80,
      "severity": "HIGH",
      "has_leakage": true
    }
  ]
}
```

Notes:

- `severity` is a backend filter
- `search` performs case-insensitive matching across `record_id`, `contract_id`, `customer_id`, and `product_id`

### `GET /records/{record_id}`

Returns a single record.

Error behavior:

- returns `404` if the record is not present in the runtime query store

## Analysis

### `GET /records/{record_id}/analysis`

Returns analysis versions for a given record.

Current response model:

- a list of `AnalysisResult`

Each `AnalysisResult` contains:

- `record_id`
- `issues`
- `has_leakage`
- `total_leakage_amount`
- `analysis_status`
- `analyzer_type`
- `analysis_version`

Each incident inside `issues` uses the richer structured shape:

- `id`
- `issue`
- `expected_amount`
- `billed_amount`
- `leakage`
- `reasoning`
- `severity`
- `suggestion`
- `confidence_score`

Example incident:

```json
{
  "id": "r_0001",
  "issue": "RATE_MISMATCH",
  "expected_amount": 1000,
  "billed_amount": 920,
  "leakage": 80,
  "reasoning": "Contract rate exceeds the billed rate, causing underbilling.",
  "severity": "HIGH",
  "suggestion": "Update the invoice rate to match the contract and recover the shortfall.",
  "confidence_score": 0.97
}
```

Error behavior:

- returns `404` if no analysis exists for the record

## Dashboard

### `GET /dashboard/summary`

Returns a lightweight aggregated summary computed from the runtime query store.

Response fields:

- `total_records`
- `flagged_records`
- `total_leakage_amount`
- `high_severity_count`
- `data_source`

Example response:

```json
{
  "total_records": 12,
  "flagged_records": 5,
  "total_leakage_amount": 1135.0,
  "high_severity_count": 2,
  "data_source": "memory"
}
```

## Current API Boundaries

Important implementation notes:

- writes run through repository classes and `DynamoDBService`
- read-side endpoints are served from the process-local runtime store
- local tests exercise the repository layer through the in-memory `runtime_dynamo_client`
