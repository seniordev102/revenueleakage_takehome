from __future__ import annotations

from ..core.exceptions import NotFoundError
from ..schemas.common import AnalysisResult
from ..stores.runtime_store import RuntimeStore


class AnalysisQueryService:
    def __init__(self, store: RuntimeStore) -> None:
        self._store = store

    def get_record_analysis(self, record_id: str) -> list[AnalysisResult]:
        results = self._store.get_analysis_results(record_id)
        if results is None:
            raise NotFoundError("Analysis not found")
        return results
