from textwrap import dedent

from app.utils.csv_parser import parse_csv_bytes
from app.utils.json_parser import parse_json_bytes


def test_parse_csv_bytes_basic():
    csv_text = dedent(
        """
        contract_id,customer_id,product_id,agreed_rate,billed_rate,quantity,expected_amount,billed_amount,discount,tax,currency,billing_date,contract_start_date,contract_end_date,region
        C-001,CU-100,P-101,100,92,10,1000,920,0,0,USD,2026-03-25,2026-01-01,2026-12-31,US
        """
    ).lstrip()

    records = parse_csv_bytes(csv_text.encode("utf-8"))
    assert len(records) == 1
    record = records[0]
    assert record.contract_id == "C-001"
    assert record.agreed_rate == 100.0
    assert record.billed_amount == 920.0


def test_parse_json_bytes_list_payload():
    json_bytes = b"""
    [
      {
        "contract_id": "C-001",
        "customer_id": "CU-100",
        "product_id": "P-101",
        "agreed_rate": 100,
        "billed_rate": 92,
        "quantity": 10,
        "expected_amount": 1000,
        "billed_amount": 920,
        "discount": 0,
        "tax": 0,
        "currency": "USD"
      }
    ]
    """
    records = parse_json_bytes(json_bytes)
    assert len(records) == 1
    record = records[0]
    assert record.contract_id == "C-001"
    assert record.agreed_rate == 100.0
    assert record.currency == "USD"

