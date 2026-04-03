from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident


def run_manual_override_checks(record: BillingRecord) -> List[AnalysisIssue]:
    issues: List[AnalysisIssue] = []

    if not record.manual_override:
        return issues

    if (
        record.expected_amount is not None
        and record.billed_amount is not None
        and record.billed_amount < record.expected_amount
    ) or (
        record.agreed_rate is not None
        and record.billed_rate is not None
        and record.billed_rate < record.agreed_rate
    ):
        issues.append(
            build_incident(
                record,
                issue=IssueType.MANUAL_OVERRIDE_ERROR,
                severity=Severity.HIGH,
                reasoning="A manual override is present and the billed values are lower than the contract-calculated values.",
                leakage=max((record.expected_amount or 0) - (record.billed_amount or 0), 0),
                suggestion="Audit the manual override approval trail and restore the approved contract pricing or quantity.",
            )
        )

    return issues
