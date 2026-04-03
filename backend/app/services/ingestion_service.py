from __future__ import annotations

import uuid
from datetime import date
from typing import List, Tuple

from ..schemas.common import BillingRecord, Upload
from ..utils.csv_parser import parse_csv_bytes
from ..utils.json_parser import parse_json_bytes
from ..utils.money import compute_expected_amount


class IngestionService:
    """
    Service responsible for:
    - parsing raw files
    - normalizing numeric fields
    - attaching upload metadata
    For Phase 3 this keeps results in memory and returns them to the caller.
    """

    def ingest_file(self, file_name: str, file_type: str, raw_bytes: bytes) -> Tuple[Upload, List[BillingRecord]]:
        upload_id = f"u_{uuid.uuid4().hex[:8]}"

        if file_type == "csv":
            records = parse_csv_bytes(raw_bytes)
        elif file_type == "json":
            records = parse_json_bytes(raw_bytes)
        else:
            raise ValueError("Unsupported file type")

        normalized = [self._normalize_record(r, upload_id, idx) for idx, r in enumerate(records, start=1)]

        upload = Upload(
            upload_id=upload_id,
            file_name=file_name,
            file_type=file_type,
            s3_key=None,  # wired to S3 in later phases
            status="INGESTED",
            uploaded_at=date.today(),
            record_count=len(normalized),
        )

        return upload, normalized

    def ingest_records(
        self,
        *,
        file_name: str,
        file_type: str,
        records: List[BillingRecord],
    ) -> Tuple[Upload, List[BillingRecord]]:
        upload_id = f"u_{uuid.uuid4().hex[:8]}"
        normalized = [self._normalize_record(r, upload_id, idx) for idx, r in enumerate(records, start=1)]

        upload = Upload(
            upload_id=upload_id,
            file_name=file_name,
            file_type=file_type,
            s3_key=None,
            status="INGESTED",
            uploaded_at=date.today(),
            record_count=len(normalized),
        )

        return upload, normalized

    def _normalize_record(self, record: BillingRecord, upload_id: str, index: int) -> BillingRecord:
        expected = record.expected_amount
        if expected is None and record.agreed_rate is not None and record.quantity is not None:
            expected = compute_expected_amount(record.agreed_rate, record.quantity)

        return BillingRecord(
            upload_id=upload_id,
            record_id=f"r_{index:04d}",
            contract_id=record.contract_id,
            customer_id=record.customer_id,
            product_id=record.product_id,
            agreed_rate=record.agreed_rate,
            billed_rate=record.billed_rate,
            quantity=record.quantity,
            expected_amount=expected,
            billed_amount=record.billed_amount,
            discount=record.discount,
            tax=record.tax,
            currency=record.currency,
            billing_date=record.billing_date,
            contract_start_date=record.contract_start_date,
            contract_end_date=record.contract_end_date,
            region=record.region,
            tier_pricing=record.tier_pricing,
            manual_override=record.manual_override,
        )

