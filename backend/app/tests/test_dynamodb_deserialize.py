from app.utils.dynamodb_deserialize import billing_record_from_ddb_item


def test_billing_record_from_minimal_ddb_item():
    item = {
        "pk": {"S": "UPLOAD#u1"},
        "sk": {"S": "RECORD#r0001"},
        "entity_type": {"S": "BILLING_RECORD"},
        "upload_id": {"S": "u1"},
        "record_id": {"S": "r0001"},
        "contract_id": {"S": "C-001"},
        "customer_id": {"S": "CU-100"},
        "product_id": {"S": "P-101"},
        "agreed_rate": {"N": "100"},
        "billed_rate": {"N": "92"},
        "quantity": {"N": "10"},
        "expected_amount": {"N": "1000"},
        "billed_amount": {"N": "920"},
        "discount": {"N": "0"},
        "tax": {"N": "0"},
        "currency": {"S": "USD"},
        "billing_date": {"S": "2026-03-25"},
        "has_leakage": {"BOOL": True},
        "leakage_amount": {"N": "80"},
        "severity": {"S": "HIGH"},
    }
    r = billing_record_from_ddb_item(item)
    assert r.record_id == "r0001"
    assert r.leakage_amount == 80.0
    assert r.severity == "HIGH"
    assert r.has_leakage is True
