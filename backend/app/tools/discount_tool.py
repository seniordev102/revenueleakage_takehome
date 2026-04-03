from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident


def run_discount_checks(record: BillingRecord) -> List[AnalysisIssue]:
    issues: List[AnalysisIssue] = []

    if record.discount is not None and record.discount < 0:
        issues.append(
            build_incident(
                record,
                issue=IssueType.DISCOUNT_MISMATCH,
                severity=Severity.MEDIUM,
                reasoning="A negative discount was applied, which is not expected for normal billing.",
                suggestion="Review manual discount overrides and restore the approved discount value.",
            )
        )

    if record.discount is not None and record.discount > 100:
        issues.append(
            build_incident(
                record,
                issue=IssueType.DISCOUNT_MISMATCH,
                severity=Severity.HIGH,
                reasoning="The discount exceeds 100%, which would over-credit or fully erase revenue.",
                suggestion="Correct the discount configuration or approval rule and rebill the impacted invoice.",
            )
        )

    return issues

