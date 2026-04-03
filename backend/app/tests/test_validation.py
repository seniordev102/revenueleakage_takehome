from datetime import date

from app.schemas.common import BillingRecord
from app.utils.validation import is_duplicate_record, required_fields_present


def make_record(**overrides) -> BillingRecord:
    base = dict(
        contract_id="C-001",
        customer_id="CU-100",
        product_id="P-101",
        agreed_rate=100.0,
        billed_rate=92.0,
        quantity=10,
        expected_amount=1000.0,
        billed_amount=920.0,
        discount=0.0,
        tax=0.0,
        currency="USD",
        billing_date=date(2026, 3, 25),
        contract_start_date=date(2026, 1, 1),
        contract_end_date=date(2026, 12, 31),
        region="US",
    )
    base.update(overrides)
    return BillingRecord(**base)


def test_required_fields_present_all_present():
    record = make_record()
    ok, missing = required_fields_present(record, ["contract_id", "customer_id"])
    assert ok is True
    assert missing == []


def test_required_fields_present_some_missing():
    record = make_record(contract_id=None)
    ok, missing = required_fields_present(record, ["contract_id", "customer_id"])
    assert ok is False
    assert missing == ["contract_id"]


def test_is_duplicate_record_detects_duplicates():
    seen: set[tuple] = set()
    r1 = make_record()
    r2 = make_record()

    assert is_duplicate_record(r1, seen) is False
    assert is_duplicate_record(r2, seen) is True


def test_is_duplicate_record_treats_different_values_as_unique():
    seen: set[tuple] = set()
    r1 = make_record()
    r2 = make_record(billed_amount=930.0)

    assert is_duplicate_record(r1, seen) is False
    assert is_duplicate_record(r2, seen) is False

