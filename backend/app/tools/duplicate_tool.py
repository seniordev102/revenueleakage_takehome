from __future__ import annotations

from typing import Iterable, List

from ..models.enums import IssueType, Severity
from ..schemas.common import AnalysisIssue, BillingRecord
from .incident_factory import build_incident
from ..utils.validation import is_duplicate_record


def run_duplicate_checks(records: Iterable[BillingRecord]) -> List[AnalysisIssue]:
    """
    Given a batch of records, detect duplicates based on the heuristic key used
    in validation utils. Returns issues associated with the second and later duplicates.
    """
    issues: List[AnalysisIssue] = []
    seen_keys: set[tuple] = set()

    for record in records:
        if is_duplicate_record(record, seen_keys):
            issues.append(
                build_incident(
                    record,
                    issue=IssueType.DUPLICATE_ENTRY,
                    severity=Severity.MEDIUM,
                    reasoning="A duplicate billing entry was detected for the same record signature.",
                    suggestion="Review duplicate adjustments or repeated invoice lines and remove the extra charge.",
                )
            )

    return issues

