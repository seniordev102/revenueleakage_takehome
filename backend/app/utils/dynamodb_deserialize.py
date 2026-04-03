"""Convert DynamoDB low-level AttributeValue items into Pydantic BillingRecord."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from boto3.dynamodb.types import TypeDeserializer

from ..schemas.common import BillingRecord

_deserializer = TypeDeserializer()


def ddb_item_to_plain(item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _deserializer.deserialize(v) for k, v in item.items()}


def _num(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (int, float)):
        return float(val)
    return float(val)


def _parse_date(val: Any) -> Optional[date]:
    if val is None or val == "":
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    s = str(val)[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def billing_record_from_ddb_item(item: Dict[str, Any]) -> BillingRecord:
    """Build BillingRecord from low-level DynamoDB item (AttributeValue format)."""
    raw = ddb_item_to_plain(item)
    return BillingRecord(
        upload_id=raw.get("upload_id"),
        record_id=raw.get("record_id"),
        contract_id=raw.get("contract_id") or None,
        customer_id=raw.get("customer_id") or None,
        product_id=raw.get("product_id") or None,
        agreed_rate=_num(raw.get("agreed_rate")),
        billed_rate=_num(raw.get("billed_rate")),
        quantity=_num(raw.get("quantity")),
        expected_amount=_num(raw.get("expected_amount")),
        billed_amount=_num(raw.get("billed_amount")),
        discount=_num(raw.get("discount")),
        tax=_num(raw.get("tax")),
        currency=raw.get("currency") or None,
        billing_date=_parse_date(raw.get("billing_date")),
        contract_start_date=_parse_date(raw.get("contract_start_date")),
        contract_end_date=_parse_date(raw.get("contract_end_date")),
        region=raw.get("region") or None,
        has_leakage=raw.get("has_leakage"),
        leakage_amount=_num(raw.get("leakage_amount")),
        severity=raw.get("severity") or None,
    )
