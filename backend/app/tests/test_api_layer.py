from fastapi.testclient import TestClient

from app.dependencies import get_runtime_store
from app.main import create_app
from app.services.runtime_dynamo import runtime_dynamo_client


client = TestClient(create_app())


def setup_function():
    get_runtime_store().clear()
    runtime_dynamo_client.items.clear()
    runtime_dynamo_client.put_calls.clear()
    runtime_dynamo_client.update_calls.clear()


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_records_empty_payload():
    resp = client.get("/records")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_upload_rejects_unsupported_file_type_with_structured_error():
    resp = client.post("/uploads", files={"file": ("sample.txt", b"bad", "text/plain")})
    assert resp.status_code == 400
    assert resp.json() == {
        "error": {
            "code": "INGESTION_ERROR",
            "message": "Unsupported file type. Use CSV or JSON.",
        }
    }


def test_dashboard_summary_endpoint():
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert {
        "total_records",
        "flagged_records",
        "total_leakage_amount",
        "high_severity_count",
    }.issubset(body.keys())
    assert body["data_source"] in {"memory", "dynamodb"}


def test_upload_creates_records_and_analysis_results():
    payload = b"""
    [
      {
        "contract_id": "C-001",
        "customer_id": "CU-100",
        "product_id": "P-ALPHA",
        "agreed_rate": 100,
        "billed_rate": 92,
        "quantity": 10,
        "expected_amount": 1000,
        "billed_amount": 920,
        "discount": 0,
        "tax": 0,
        "currency": "USD",
        "billing_date": "2026-03-25",
        "contract_start_date": "2026-01-01",
        "contract_end_date": "2026-12-31",
        "region": "US"
      }
    ]
    """

    resp = client.post("/uploads", files={"file": ("sample.json", payload, "application/json")})
    assert resp.status_code == 200

    body = resp.json()
    assert body["record_count"] == 1
    assert len(get_runtime_store().list_records()) == 1

    record_id = get_runtime_store().list_records()[0].record_id
    assert record_id is not None
    analysis = get_runtime_store().get_analysis_results(record_id)[0]
    assert analysis.has_leakage is True
    assert any(issue.issue == "RATE_MISMATCH" for issue in analysis.issues)

    analysis_resp = client.get(f"/records/{record_id}/analysis")
    assert analysis_resp.status_code == 200
    assert analysis_resp.json()[0]["record_id"] == record_id

    assert len(runtime_dynamo_client.put_calls) >= 3
    assert len(runtime_dynamo_client.update_calls) >= 1


def test_list_records_supports_backend_search_filter():
    payload = b"""
    [
      {
        "contract_id": "C-001",
        "customer_id": "CU-100",
        "product_id": "P-ALPHA",
        "agreed_rate": 100,
        "billed_rate": 92,
        "quantity": 10,
        "expected_amount": 1000,
        "billed_amount": 920,
        "discount": 0,
        "tax": 0,
        "currency": "USD",
        "billing_date": "2026-03-25",
        "contract_start_date": "2026-01-01",
        "contract_end_date": "2026-12-31",
        "region": "US"
      },
      {
        "contract_id": "C-002",
        "customer_id": "CU-101",
        "product_id": "P-BETA",
        "agreed_rate": 50,
        "billed_rate": 50,
        "quantity": 5,
        "expected_amount": 250,
        "billed_amount": 250,
        "discount": 0,
        "tax": 0,
        "currency": "USD",
        "billing_date": "2026-03-26",
        "contract_start_date": "2026-01-01",
        "contract_end_date": "2026-12-31",
        "region": "US"
      }
    ]
    """

    client.post("/uploads", files={"file": ("sample.json", payload, "application/json")})

    resp = client.get("/records?search=beta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["product_id"] == "P-BETA"


def test_rest_api_ingestion_accepts_json_body():
    resp = client.post(
        "/uploads/records",
        json=[
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
                "region": "US",
            }
        ],
    )
    assert resp.status_code == 200

    body = resp.json()
    assert body["upload"]["file_type"] == "api"
    assert body["record_count"] == 1
    assert len(get_runtime_store().list_records()) == 1

