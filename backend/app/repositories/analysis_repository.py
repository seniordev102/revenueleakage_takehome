from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..schemas.common import AnalysisResult
from ..services.dynamodb_service import DynamoDBService


class AnalysisRepository:
    def __init__(self, dynamo: DynamoDBService) -> None:
        self._dynamo = dynamo

    def create_analysis_item(self, upload_id: str, result: AnalysisResult) -> Dict:
        created_at = datetime.now(timezone.utc).isoformat()
        sk = f"ANALYSIS#{result.record_id}#v{result.analysis_version}"
        item = {
            "pk": {"S": f"UPLOAD#{upload_id}"},
            "sk": {"S": sk},
            "entity_type": {"S": "ANALYSIS_RESULT"},
            "upload_id": {"S": upload_id},
            "record_id": {"S": result.record_id},
            "analysis_version": {"N": str(result.analysis_version)},
            "issues": {"L": [issue.model_dump(mode="python") for issue in result.issues]},
            "has_leakage": {"BOOL": result.has_leakage},
            "total_leakage_amount": {"N": str(result.total_leakage_amount)},
            "analysis_status": {"S": result.analysis_status},
            "analyzer_type": {"S": result.analyzer_type},
            "created_at": {"S": created_at},
        }
        self._dynamo.put(item)
        return item

