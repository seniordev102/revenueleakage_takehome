from datetime import date

from app.schemas.common import BillingRecord
from app.tools.contract_tool import run_contract_checks
from app.tools.discount_tool import run_discount_checks
from app.tools.duplicate_tool import run_duplicate_checks
from app.tools.manual_override_tool import run_manual_override_checks
from app.tools.quantity_tool import run_quantity_checks
from app.tools.tax_tool import run_tax_checks


def make_record(**overrides) -> BillingRecord:
    base = dict(
        contract_id="C-001",
        customer_id="CU-100",
        product_id="P-101",
        agreed_rate=100,
        billed_rate=100,
        quantity=10,
        expected_amount=1000,
        billed_amount=1000,
        discount=0,
        tax=0,
        currency="USD",
        billing_date=date(2026, 3, 25),
        contract_start_date=date(2026, 1, 1),
        contract_end_date=date(2026, 12, 31),
        region="US",
    )
    base.update(overrides)
    return BillingRecord(**base)


def test_quantity_checks_detect_negative_pricing_and_zero_billing():
    r1 = make_record(quantity=-5)
    issues1 = run_quantity_checks(r1)
    assert any(i.issue_type == "NEGATIVE_PRICING" for i in issues1)

    r2 = make_record(billed_amount=0, expected_amount=900)
    issues2 = run_quantity_checks(r2)
    zero_issues = [i for i in issues2 if i.issue_type == "ZERO_BILLING"]
    assert len(zero_issues) == 1
    assert zero_issues[0].leakage_amount == 900

    r3 = make_record(quantity=10, agreed_rate=100, billed_rate=100, expected_amount=1000, billed_amount=1200)
    issues3 = run_quantity_checks(r3)
    assert any(i.issue_type == "QUANTITY_MISMATCH" for i in issues3)


def test_discount_checks_detect_invalid_discounts():
    r1 = make_record(discount=-5)
    issues1 = run_discount_checks(r1)
    assert any(i.issue_type == "DISCOUNT_MISMATCH" for i in issues1)

    r2 = make_record(discount=150)
    issues2 = run_discount_checks(r2)
    assert any(i.issue_type == "DISCOUNT_MISMATCH" and i.severity == "HIGH" for i in issues2)


def test_tax_checks_detect_mismatch_for_region():
    # For US region, EXPECTED_TAX_RATES = 0.0 so any non-zero tax will trigger an issue
    r = make_record(tax=5, billed_amount=1000, region="US")
    issues = run_tax_checks(r)
    assert any(i.issue_type == "TAX_MISMATCH" for i in issues)


def test_duplicate_checks_detect_second_duplicate():
    r1 = make_record(contract_id="C-005")
    r2 = make_record(contract_id="C-005")
    issues = run_duplicate_checks([r1, r2])
    assert len(issues) == 1
    assert issues[0].issue_type == "DUPLICATE_ENTRY"


def test_contract_checks_detect_out_of_contract_and_tier_pricing_mismatch():
    out_of_contract = make_record(
        billing_date=date(2027, 1, 10),
        contract_end_date=date(2026, 12, 31),
    )
    out_issues = run_contract_checks(out_of_contract)
    assert any(i.issue_type == "OUT_OF_CONTRACT_BILLING" for i in out_issues)

    tier_pricing = make_record(
        quantity=150,
        billed_rate=10,
        billed_amount=1500,
        tier_pricing={"threshold": 100, "discounted_rate": 9},
    )
    tier_issues = run_contract_checks(tier_pricing)
    assert any(i.issue_type == "TIER_PRICING_MISMATCH" for i in tier_issues)


def test_manual_override_checks_detect_override_error():
    record = make_record(
        manual_override=True,
        agreed_rate=100,
        billed_rate=90,
        expected_amount=1000,
        billed_amount=900,
    )
    issues = run_manual_override_checks(record)
    assert any(i.issue_type == "MANUAL_OVERRIDE_ERROR" for i in issues)

