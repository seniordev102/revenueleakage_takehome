from __future__ import annotations

import json
from typing import List

from .money import safe_float
from ..schemas.common import BillingRecord


def parse_json_bytes(raw_bytes: bytes) -> List[BillingRecord]:
    """
    Parse JSON bytes into BillingRecord instances.
    Accepts either a list of objects or a single object.
    """
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid JSON payload") from exc

    items = payload if isinstance(payload, list) else [payload]

    records: List[BillingRecord] = []
    for row in items:
        data = {
            "contract_id": row.get("contract_id"),
            "customer_id": row.get("customer_id"),
            "product_id": row.get("product_id"),
            "agreed_rate": safe_float(row.get("agreed_rate")),
            "billed_rate": safe_float(row.get("billed_rate")),
            "quantity": safe_float(row.get("quantity")),
            "expected_amount": safe_float(row.get("expected_amount")),
            "billed_amount": safe_float(row.get("billed_amount")),
            "discount": safe_float(row.get("discount")),
            "tax": safe_float(row.get("tax")),
            "currency": row.get("currency"),
            "billing_date": row.get("billing_date"),
            "contract_start_date": row.get("contract_start_date"),
            "contract_end_date": row.get("contract_end_date"),
            "region": row.get("region"),
            "tier_pricing": row.get("tier_pricing"),
            "manual_override": row.get("manual_override"),
        }
        records.append(BillingRecord(**data))
    return records

