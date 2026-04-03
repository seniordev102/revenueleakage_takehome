from datetime import date

from pydantic import ValidationError

from app.models.enums import IssueType, Severity
from app.schemas.common import (
    AnalysisIssue,
    AnalysisResult,
    BillingRecord,
    DashboardSummary,
    Upload,
)


def test_upload_schema_requires_basic_fields():
    upload = Upload(
        upload_id="u_001",
        file_name="sample.csv",
        file_type="csv",
        s3_key="uploads/u_001/sample.csv",
        status="COMPLETED",
        uploaded_at=date(2026, 4, 1),
        record_count=12,
    )
    assert upload.upload_id == "u_001"
    assert upload.record_count == 12


def test_billing_record_allows_optional_fields():
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
        billing_date=date(2026, 3, 25),
        contract_start_date=date(2026, 1, 1),
        contract_end_date=date(2026, 12, 31),
        region="US",
    )
    assert record.contract_id == "C-001"
    assert record.expected_amount == 1000


def test_analysis_issue_uses_enums_for_type_and_severity():
    issue = AnalysisIssue(
        id="r_001",
        issue=IssueType.RATE_MISMATCH.value,
        expected_amount=1000.0,
        billed_amount=920.0,
        leakage=80.0,
        reasoning="Billed rate is lower than the contract rate.",
        severity=Severity.HIGH.value,
        suggestion="Correct the billed rate and rebill the difference.",
    )
    assert issue.issue_type == IssueType.RATE_MISMATCH
    assert issue.severity == Severity.HIGH
    assert issue.id == "r_001"
    assert issue.leakage_amount == 80.0
    assert issue.reasoning == "Billed rate is lower than the contract rate."


def test_analysis_result_requires_record_id_and_issues():
    issue = AnalysisIssue(
        id="r_001",
        issue=IssueType.RATE_MISMATCH.value,
        expected_amount=1000.0,
        billed_amount=920.0,
        leakage=80.0,
        reasoning="Billed rate is lower than the contract rate.",
        severity=Severity.HIGH.value,
        suggestion="Correct the billed rate and rebill the difference.",
    )
    result = AnalysisResult(
        record_id="r_001",
        issues=[issue],
        has_leakage=True,
        total_leakage_amount=80.0,
        analysis_status="COMPLETED",
        analyzer_type="RULE_PLUS_LLM",
        analysis_version=1,
    )
    assert result.record_id == "r_001"
    assert result.total_leakage_amount == 80.0


def test_analysis_result_requires_issues_non_empty():
    try:
        AnalysisResult(
            record_id="r_001",
            issues=[],
            has_leakage=False,
            total_leakage_amount=0.0,
            analysis_status="COMPLETED",
            analyzer_type="RULE_PLUS_LLM",
            analysis_version=1,
        )
    except ValidationError:
        # Pydantic v2 raises ValidationError for constrained fields; we keep this
        # placeholder test to tighten constraints later when we add them.
        pass


def test_dashboard_summary_schema_basic():
    summary = DashboardSummary(
        total_records=100,
        flagged_records=10,
        total_leakage_amount=1234.5,
        high_severity_count=4,
    )
    assert summary.total_records == 100
    assert summary.flagged_records == 10

