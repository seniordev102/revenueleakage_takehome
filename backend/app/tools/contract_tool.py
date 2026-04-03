from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident


def run_contract_checks(record: BillingRecord) -> List[AnalysisIssue]:
    issues: List[AnalysisIssue] = []

    if (
        record.billing_date is not None
        and record.contract_start_date is not None
        and record.billing_date < record.contract_start_date
    ) or (
        record.billing_date is not None
        and record.contract_end_date is not None
        and record.billing_date > record.contract_end_date
    ):
        issues.append(
            build_incident(
                record,
                issue=IssueType.OUT_OF_CONTRACT_BILLING,
                severity=Severity.HIGH,
                reasoning="Billing date falls outside the contract term, so the invoice may not be contract-compliant.",
                leakage=record.billed_amount,
                suggestion="Validate contract dates and rebill only the eligible usage period.",
            )
        )

    tier = record.tier_pricing or {}
    threshold = tier.get("threshold")
    discounted_rate = tier.get("discounted_rate")
    if (
        threshold is not None
        and discounted_rate is not None
        and record.quantity is not None
        and record.quantity >= float(threshold)
        and record.billed_rate is not None
        and abs(record.billed_rate - float(discounted_rate)) > 0.01
    ):
        expected_amount = float(discounted_rate) * record.quantity
        billed_amount = record.billed_amount
        leakage = None
        if billed_amount is not None:
            leakage = max(expected_amount - billed_amount, 0.0)
        issues.append(
            build_incident(
                record,
                issue=IssueType.TIER_PRICING_MISMATCH,
                severity=Severity.MEDIUM,
                reasoning="Tiered pricing rules appear to have been missed for the billed quantity.",
                expected_amount=expected_amount,
                billed_amount=billed_amount,
                leakage=leakage,
                suggestion="Apply the contracted tier rate for the usage threshold and correct the invoice.",
            )
        )

    return issues
