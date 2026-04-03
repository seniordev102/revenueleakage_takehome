from typing import Iterable, List, Tuple

from ..schemas.common import BillingRecord


def required_fields_present(record: BillingRecord, fields: Iterable[str]) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    for field in fields:
        if getattr(record, field, None) is None:
            missing.append(field)
    return (len(missing) == 0, missing)


def is_duplicate_record(record: BillingRecord, seen_keys: set[tuple]) -> bool:
    """
    Simple duplicate heuristic based on (contract_id, customer_id, product_id, billing_date, billed_amount).
    """
    key = (
        record.contract_id,
        record.customer_id,
        record.product_id,
        record.billing_date,
        record.billed_amount,
    )
    if key in seen_keys:
        return True
    seen_keys.add(key)
    return False

