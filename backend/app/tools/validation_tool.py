from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident
from ..utils.validation import required_fields_present


def run_validation_checks(record: BillingRecord) -> List[AnalysisIssue]:
    """
    Perform basic validation checks on required fields.
    """
    issues: List[AnalysisIssue] = []

    ok, missing = required_fields_present(
        record,
        ["contract_id", "customer_id", "product_id", "currency", "billing_date"],
    )
    if not ok:
        issues.append(
            build_incident(
                record,
                issue=IssueType.MISSING_CONTRACT_RATE,
                severity=Severity.HIGH,
                reasoning=f"Missing required fields: {', '.join(missing)}.",
                suggestion="Complete the missing contract or invoice fields before relying on this billing result.",
            )
        )

    return issues

