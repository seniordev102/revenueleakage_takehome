from __future__ import annotations

from typing import List

from ..schemas.common import AnalysisResult, BillingRecord


class RuntimeStore:
    def __init__(self) -> None:
        self._records: dict[str, BillingRecord] = {}
        self._analysis_results: dict[str, list[AnalysisResult]] = {}

    def clear(self) -> None:
        self._records.clear()
        self._analysis_results.clear()

    def list_records(self) -> List[BillingRecord]:
        return list(self._records.values())

    def upsert_record(self, key: str, record: BillingRecord) -> None:
        self._records[key] = record

    def get_record(self, record_id: str) -> BillingRecord | None:
        return self._records.get(record_id)

    def set_analysis_results(self, record_id: str, results: list[AnalysisResult]) -> None:
        self._analysis_results[record_id] = results

    def get_analysis_results(self, record_id: str) -> list[AnalysisResult] | None:
        return self._analysis_results.get(record_id)
