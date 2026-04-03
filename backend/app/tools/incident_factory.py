from __future__ import annotations

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord


def build_incident(
    record: BillingRecord,
    *,
    issue: IssueType | str,
    severity: Severity | str,
    reasoning: str,
    leakage: float | None = None,
    suggestion: str | None = None,
    expected_amount: float | None = None,
    billed_amount: float | None = None,
) -> AnalysisIssue:
    issue_value = issue.value if isinstance(issue, IssueType) else issue
    severity_value = severity.value if isinstance(severity, Severity) else severity

    incident_id = (
        record.record_id
        or record.contract_id
        or record.customer_id
        or record.product_id
        or "unknown-record"
    )

    return AnalysisIssue(
        id=incident_id,
        issue=issue_value,
        expected_amount=record.expected_amount if expected_amount is None else expected_amount,
        billed_amount=record.billed_amount if billed_amount is None else billed_amount,
        leakage=leakage,
        reasoning=reasoning,
        severity=severity_value,
        suggestion=suggestion,
    )
