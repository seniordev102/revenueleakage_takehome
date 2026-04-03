from __future__ import annotations

from typing import List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident
from ..utils.money import compute_expected_amount, compute_leakage_amount


def run_pricing_checks(record: BillingRecord) -> List[AnalysisIssue]:
    """
    Pricing-related checks.

    Important: avoid double-counting leakage for the same underlying issue.
    If a rate mismatch is already detected, we do not emit an additional
    expected-vs-billed difference issue for the same shortfall.
    """
    issues: List[AnalysisIssue] = []
    has_rate_mismatch = False
    has_quantity_mismatch = False

    if record.agreed_rate is not None and record.billed_rate is not None:
        if record.billed_rate < record.agreed_rate:
            leakage_amount = compute_leakage_amount(
                compute_expected_amount(record.agreed_rate, record.quantity or 0),
                record.billed_amount or 0,
            )
            issues.append(
                build_incident(
                    record,
                    issue=IssueType.RATE_MISMATCH,
                    severity=Severity.HIGH,
                    reasoning="Billed rate is lower than the agreed contract rate.",
                    leakage=leakage_amount,
                    suggestion="Correct the billing rate to the contract rate and rebill the shortfall.",
                )
            )
            has_rate_mismatch = True

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
        has_quantity_mismatch = abs(implied_billed_quantity - record.quantity) > 0.01

    if (
        record.expected_amount is not None
        and record.billed_amount is not None
        and not has_rate_mismatch
        and not has_quantity_mismatch
        and record.billed_amount < record.expected_amount
    ):
        leakage_amount = compute_leakage_amount(record.expected_amount, record.billed_amount)
        issues.append(
            build_incident(
                record,
                issue=IssueType.EXPECTED_VS_BILLED_DIFFERENCE,
                severity=Severity.MEDIUM,
                reasoning="Billed amount is lower than the expected amount for this record.",
                leakage=leakage_amount,
                suggestion="Compare the invoice amount to the contract calculation and bill the missing amount.",
            )
        )

    expected_currency_by_region = {"US": "USD", "EU": "EUR"}
    if (
        record.currency
        and record.region in expected_currency_by_region
        and record.currency != expected_currency_by_region[record.region]
    ):
        issues.append(
            build_incident(
                record,
                issue=IssueType.CURRENCY_MISMATCH,
                severity=Severity.MEDIUM,
                reasoning=f"Currency {record.currency} does not match the expected currency for region {record.region}.",
                suggestion="Verify the contract currency and recheck any FX conversion applied during billing.",
            )
        )
    elif record.currency and record.currency not in {"USD", "EUR"}:
        issues.append(
            build_incident(
                record,
                issue=IssueType.CURRENCY_MISMATCH,
                severity=Severity.INFO,
                reasoning=f"Unexpected currency {record.currency} was used for this billing record.",
                suggestion="Verify the contract currency and applied FX conversion before finalizing the invoice.",
            )
        )

    return issues


