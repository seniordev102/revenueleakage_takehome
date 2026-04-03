from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident


def run_quantity_checks(record: BillingRecord) -> List[AnalysisIssue]:
    issues: List[AnalysisIssue] = []

    if record.quantity is not None and record.quantity < 0:
        issues.append(
            build_incident(
                record,
                issue=IssueType.NEGATIVE_PRICING,
                severity=Severity.HIGH,
                reasoning="The billed quantity is negative, which suggests a pricing or manual adjustment error.",
                suggestion="Audit the source transaction and reverse any invalid manual quantity override.",
            )
        )

    if record.billed_amount is not None and record.billed_amount == 0 and (record.expected_amount or 0) > 0:
        issues.append(
            build_incident(
                record,
                issue=IssueType.ZERO_BILLING,
                severity=Severity.HIGH,
                reasoning="The record has a non-zero expected charge, but the billed amount is zero.",
                leakage=record.expected_amount,
                suggestion="Bill the missing charge and validate that the product or usage line was not suppressed.",
            )
        )

    if (
        record.quantity is not None
        and record.quantity >= 0
        and record.billed_rate not in (None, 0)
        and record.agreed_rate is not None
        and record.billed_amount is not None
        and record.expected_amount is not None
        and abs(record.billed_rate - record.agreed_rate) < 0.01
    ):
        implied_billed_quantity = record.billed_amount / record.billed_rate
        if abs(implied_billed_quantity - record.quantity) > 0.01:
            issues.append(
                build_incident(
                    record,
                    issue=IssueType.QUANTITY_MISMATCH,
                    severity=Severity.MEDIUM,
                    reasoning="Billed quantity does not align with the invoice totals for the contracted rate.",
                    leakage=max(record.expected_amount - record.billed_amount, 0.0),
                    suggestion="Validate the metered or delivered quantity and correct the invoice quantity.",
                )
            )

    return issues

