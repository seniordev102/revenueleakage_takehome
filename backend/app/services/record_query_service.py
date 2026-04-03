from __future__ import annotations

from typing import Optional

from ..core.exceptions import NotFoundError
from ..models.enums import Severity
from ..schemas.common import BillingRecord
from ..stores.runtime_store import RuntimeStore


class RecordQueryService:
    def __init__(self, store: RuntimeStore) -> None:
        self._store = store

    def list_records(
        self,
        *,
        upload_id: Optional[str],
        severity: Optional[Severity],
        flagged_only: bool,
        search: Optional[str],
        page: int,
        page_size: int,
    ) -> dict:
        records = self._filter_records(
            upload_id=upload_id,
            severity=severity,
            flagged_only=flagged_only,
            search=search,
        )
        total = len(records)
        start = max(page - 1, 0) * page_size
        end = start + page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": records[start:end],
        }

    def get_record(self, record_id: str) -> BillingRecord:
        record = self._store.get_record(record_id)
        if not record:
            raise NotFoundError("Record not found")
        return record

    def _filter_records(
        self,
        *,
        upload_id: Optional[str],
        severity: Optional[Severity],
        flagged_only: bool,
        search: Optional[str],
    ) -> list[BillingRecord]:
        records = self._store.list_records()
        if upload_id:
            records = [r for r in records if r.upload_id == upload_id]
        if severity:
            records = [r for r in records if getattr(r, "severity", None) == severity.value]
        if flagged_only:
            records = [r for r in records if getattr(r, "has_leakage", False)]
        if search:
            normalized = search.strip().lower()
            records = [
                r
                for r in records
                if any(
                    normalized in (value or "").lower()
                    for value in (r.record_id, r.contract_id, r.customer_id, r.product_id)
                )
            ]
        return records
