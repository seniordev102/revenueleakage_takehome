from app.utils.money import compute_expected_amount, compute_leakage_amount, safe_float


def test_safe_float_with_valid_values():
    assert safe_float(10) == 10.0
    assert safe_float("12.5") == 12.5


def test_safe_float_with_invalid_values():
    assert safe_float("not-a-number") is None
    assert safe_float(None) is None


def test_compute_expected_amount_basic():
    assert compute_expected_amount(100, 2) == 200.0


def test_compute_expected_amount_missing_inputs():
    assert compute_expected_amount(None, 2) is None
    assert compute_expected_amount(100, None) is None


def test_compute_leakage_amount_no_leakage_when_billed_greater_or_equal():
    assert compute_leakage_amount(1000, 1000) == 0.0
    assert compute_leakage_amount(1000, 1200) == 0.0


def test_compute_leakage_amount_when_under_billed():
    assert compute_leakage_amount(1000, 920) == 80.0


def test_compute_leakage_amount_missing_inputs():
    assert compute_leakage_amount(None, 1000) == 0.0
    assert compute_leakage_amount(1000, None) == 0.0

