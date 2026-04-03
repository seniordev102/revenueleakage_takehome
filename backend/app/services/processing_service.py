from __future__ import annotations

from typing import Any, List

from ..agents.leakage_agent import LeakageAnalysisAgent
from ..core.logging import get_logger
from ..repositories.analysis_repository import AnalysisRepository
from ..repositories.record_repository import RecordRepository
from ..repositories.upload_repository import UploadRepository
from ..schemas.common import BillingRecord, Upload
from ..stores.runtime_store import RuntimeStore
from ..tools.duplicate_tool import run_duplicate_checks

logger = get_logger(__name__)


class ProcessingService:
    def __init__(
        self,
        *,
        upload_repo: UploadRepository,
        record_repo: RecordRepository,
        analysis_repo: AnalysisRepository,
        analysis_agent: LeakageAnalysisAgent,
        store: RuntimeStore,
    ) -> None:
        self._upload_repo = upload_repo
        self._record_repo = record_repo
        self._analysis_repo = analysis_repo
        self._analysis_agent = analysis_agent
        self._store = store

    def process_records(self, upload: Upload, records: List[BillingRecord]) -> dict[str, Any]:
        logger.info("Processing upload %s with %s records", upload.upload_id, len(records))

        self._upload_repo.create_upload_item(upload)
        for record in records:
            self._record_repo.create_billing_record_item(record)

        duplicate_issues = run_duplicate_checks(records)
        duplicates_by_record_id = {issue.id: issue for issue in duplicate_issues if issue.id}

        enriched_records: List[BillingRecord] = []
        for idx, record in enumerate(records, start=1):
            result = self._analysis_agent.analyze_record(upload.upload_id, record)
            duplicate_issue = duplicates_by_record_id.get(record.record_id or "")
            if duplicate_issue is not None:
                result.issues.append(duplicate_issue)
                result.issues = self._analysis_agent._prioritize_issues(result.issues)
                result.has_leakage = result.has_leakage or (duplicate_issue.leakage or 0) > 0

            base = record.model_dump(exclude={"has_leakage", "leakage_amount", "severity"})
            enriched = BillingRecord(
                **base,
                has_leakage=result.has_leakage,
                leakage_amount=result.total_leakage_amount,
                severity=result.issues[0].severity if result.issues else "INFO",
            )
            key = enriched.record_id or f"{upload.upload_id}-{idx}"
            self._store.upsert_record(key, enriched)
            self._store.set_analysis_results(key, [result])
            enriched_records.append(enriched)

        logger.info(
            "Completed upload %s: %s processed records, %s sample records returned",
            upload.upload_id,
            len(enriched_records),
            min(3, len(enriched_records)),
        )
        return {
            "upload": upload,
            "record_count": len(enriched_records),
            "sample_records": enriched_records[:3],
        }
