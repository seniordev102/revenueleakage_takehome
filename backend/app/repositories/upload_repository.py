from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..schemas.common import Upload
from ..services.dynamodb_service import DynamoDBService


class UploadRepository:
    def __init__(self, dynamo: DynamoDBService) -> None:
        self._dynamo = dynamo

    def create_upload_item(self, upload: Upload) -> Dict:
        created_at = datetime.now(timezone.utc).isoformat()
        item = {
            "pk": {"S": f"UPLOAD#{upload.upload_id}"},
            "sk": {"S": "META"},
            "entity_type": {"S": "UPLOAD"},
            "upload_id": {"S": upload.upload_id},
            "file_name": {"S": upload.file_name},
            "file_type": {"S": upload.file_type},
            "s3_key": {"S": upload.s3_key or ""},
            "status": {"S": upload.status},
            "record_count": {"N": str(upload.record_count or 0)},
            "created_at": {"S": created_at},
        }
        self._dynamo.put(item)
        return item

