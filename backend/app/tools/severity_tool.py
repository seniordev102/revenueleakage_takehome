from __future__ import annotations

from ..models.enums import Severity


def assign_severity_from_leakage(leakage_amount: float) -> Severity:
    """
    Deterministic severity logic for a single issue based on leakage amount.
    Thresholds are simple and documented for clarity.
    """
    if leakage_amount >= 1000:
        return Severity.HIGH
    if leakage_amount >= 200:
        return Severity.MEDIUM
    if leakage_amount > 0:
        return Severity.LOW
    return Severity.INFO

