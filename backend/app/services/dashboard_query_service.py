from __future__ import annotations

from ..schemas.common import DashboardSummary
from ..stores.runtime_store import RuntimeStore


class DashboardQueryService:
    def __init__(self, store: RuntimeStore) -> None:
        self._store = store

    def get_summary(self) -> DashboardSummary:
        records = self._store.list_records()
        total_records = len(records)
        flagged_records = sum(1 for r in records if r.has_leakage)
        total_leakage_amount = sum((r.leakage_amount or 0.0) for r in records)
        high_severity_count = sum(1 for r in records if r.severity == "HIGH")
        return DashboardSummary(
            total_records=total_records,
            flagged_records=flagged_records,
            total_leakage_amount=total_leakage_amount,
            high_severity_count=high_severity_count,
        )
