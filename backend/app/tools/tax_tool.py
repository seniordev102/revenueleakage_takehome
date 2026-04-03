from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident


EXPECTED_TAX_RATES = {
    "US": 0.0,
    "EU": 0.2,
}


def run_tax_checks(record: BillingRecord) -> List[AnalysisIssue]:
    issues: List[AnalysisIssue] = []

    if record.tax is None or record.billed_amount is None:
        return issues

    if record.region in EXPECTED_TAX_RATES:
        expected_rate = EXPECTED_TAX_RATES[record.region]
        expected_tax = record.billed_amount * expected_rate
        # simple tolerance
        if abs(record.tax - expected_tax) > 0.01:
            issues.append(
                build_incident(
                    record,
                    issue=IssueType.TAX_MISMATCH,
                    severity=Severity.MEDIUM,
                    reasoning="Tax does not match the expected regional rate for this billed amount.",
                    leakage=max(expected_tax - record.tax, 0),
                    expected_amount=expected_tax,
                    billed_amount=record.tax,
                    suggestion="Recalculate tax using the contract region and rebill or credit the difference.",
                )
            )

    return issues

