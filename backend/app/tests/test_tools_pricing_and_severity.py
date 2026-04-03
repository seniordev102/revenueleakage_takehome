from app.models.enums import Severity
from app.schemas.common import BillingRecord
from app.tools.pricing_tool import run_pricing_checks
from app.tools.severity_tool import assign_severity_from_leakage


def test_rate_mismatch_detection_creates_high_severity_issue():
    record = BillingRecord(
        contract_id="C-001",
        customer_id="CU-100",
        product_id="P-101",
        agreed_rate=100,
        billed_rate=92,
        quantity=10,
        expected_amount=1000,
        billed_amount=920,
        discount=0,
        tax=0,
        currency="USD",
    )
    issues = run_pricing_checks(record)
    rate_issues = [i for i in issues if i.issue_type == "RATE_MISMATCH"]
    assert len(rate_issues) == 1
    assert rate_issues[0].severity == Severity.HIGH
    assert rate_issues[0].leakage_amount == 80.0


def test_expected_vs_billed_difference_creates_medium_severity_issue():
    record = BillingRecord(
        contract_id="C-002",
        customer_id="CU-101",
        product_id="P-102",
        agreed_rate=50,
        billed_rate=None,
        quantity=20,
        expected_amount=1000,
        billed_amount=850,
        discount=0,
        tax=0,
        currency="USD",
    )
    issues = run_pricing_checks(record)
    diff_issues = [i for i in issues if i.issue_type == "EXPECTED_VS_BILLED_DIFFERENCE"]
    assert len(diff_issues) == 1
    assert diff_issues[0].severity == Severity.MEDIUM
    assert diff_issues[0].leakage_amount == 150.0


def test_severity_assignment_thresholds():
    assert assign_severity_from_leakage(0) == Severity.INFO
    assert assign_severity_from_leakage(50) == Severity.LOW
    assert assign_severity_from_leakage(250) == Severity.MEDIUM
    assert assign_severity_from_leakage(1500) == Severity.HIGH


def test_currency_mismatch_detects_region_currency_problem():
    record = BillingRecord(
        contract_id="C-003",
        customer_id="CU-102",
        product_id="P-103",
        agreed_rate=100,
        billed_rate=100,
        quantity=1,
        expected_amount=100,
        billed_amount=100,
        discount=0,
        tax=0,
        currency="EUR",
        region="US",
    )
    issues = run_pricing_checks(record)
    currency_issues = [i for i in issues if i.issue_type == "CURRENCY_MISMATCH"]
    assert len(currency_issues) == 1
    assert currency_issues[0].severity == Severity.MEDIUM

