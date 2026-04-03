from typing import Optional


def safe_float(value: Optional[float | int | str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_expected_amount(agreed_rate: Optional[float], quantity: Optional[float]) -> Optional[float]:
    if agreed_rate is None or quantity is None:
        return None
    return float(agreed_rate) * float(quantity)


def compute_leakage_amount(expected_amount: Optional[float], billed_amount: Optional[float]) -> float:
    if expected_amount is None or billed_amount is None:
        return 0.0
    return max(float(expected_amount) - float(billed_amount), 0.0)

