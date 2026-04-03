from __future__ import annotations

import csv
from io import StringIO
from typing import List

from .money import safe_float
from ..schemas.common import BillingRecord


def parse_csv_bytes(raw_bytes: bytes) -> List[BillingRecord]:
    """
    Parse CSV bytes into BillingRecord instances.
    Assumes a header row with field names matching BillingRecord fields.
    """
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Unable to decode CSV file as UTF-8") from exc

    reader = csv.DictReader(StringIO(text))
    records: List[BillingRecord] = []
    for row in reader:
        data = {
            "contract_id": row.get("contract_id") or None,
            "customer_id": row.get("customer_id") or None,
            "product_id": row.get("product_id") or None,
            "agreed_rate": safe_float(row.get("agreed_rate")),
            "billed_rate": safe_float(row.get("billed_rate")),
            "quantity": safe_float(row.get("quantity")),
            "expected_amount": safe_float(row.get("expected_amount")),
            "billed_amount": safe_float(row.get("billed_amount")),
            "discount": safe_float(row.get("discount")),
            "tax": safe_float(row.get("tax")),
            "currency": row.get("currency") or None,
            "billing_date": row.get("billing_date") or None,
            "contract_start_date": row.get("contract_start_date") or None,
            "contract_end_date": row.get("contract_end_date") or None,
            "region": row.get("region") or None,
            "manual_override": (row.get("manual_override") or "").strip().lower() in {"true", "1", "yes"},
        }
        records.append(BillingRecord(**data))
    return records

