from datetime import date
from textwrap import dedent

from app.schemas.common import BillingRecord
from app.services.ingestion_service import IngestionService


def test_ingest_file_from_csv_assigns_upload_and_record_ids():
    csv_text = dedent(
        """
        contract_id,customer_id,product_id,agreed_rate,billed_rate,quantity,expected_amount,billed_amount,discount,tax,currency,billing_date,contract_start_date,contract_end_date,region
        C-001,CU-100,P-101,100,92,10,1000,920,0,0,USD,2026-03-25,2026-01-01,2026-12-31,US
        """
    ).lstrip()

    service = IngestionService()
    upload, records = service.ingest_file(
        file_name="sample.csv",
        file_type="csv",
        raw_bytes=csv_text.encode("utf-8"),
    )

    assert upload.file_name == "sample.csv"
    assert upload.file_type == "csv"
    assert upload.status == "INGESTED"
    assert upload.record_count == 1
    assert isinstance(upload.uploaded_at, date)

    assert len(records) == 1
    record = records[0]
    assert record.upload_id == upload.upload_id
    assert record.record_id.startswith("r_")
    assert record.expected_amount == 1000.0


def test_ingest_file_from_json_computes_expected_amount_if_missing():
    json_bytes = b"""
    [
      {
        "contract_id": "C-008",
        "customer_id": "CU-107",
        "product_id": "P-108",
        "agreed_rate": 40,
        "billed_rate": 40,
        "quantity": 10,
        "expected_amount": null,
        "billed_amount": 400,
        "discount": 0,
        "tax": 0,
        "currency": "USD"
      }
    ]
    """
    service = IngestionService()
    upload, records = service.ingest_file(
        file_name="sample.json",
        file_type="json",
        raw_bytes=json_bytes,
    )

    assert upload.file_type == "json"
    assert upload.record_count == 1

    record = records[0]
    assert record.expected_amount == 400.0


def test_ingest_records_from_api_assigns_upload_metadata():
    service = IngestionService()
    upload, records = service.ingest_records(
        file_name="api-ingest",
        file_type="api",
        records=[
            BillingRecord(
                contract_id="C-009",
                customer_id="CU-108",
                product_id="P-109",
                agreed_rate=10,
                quantity=5,
                billed_amount=45,
            )
        ],
    )

    assert upload.file_type == "api"
    assert upload.record_count == 1
    assert records[0].upload_id == upload.upload_id
    assert records[0].expected_amount == 50.0

