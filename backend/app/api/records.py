from typing import Any, Optional

from fastapi import APIRouter, Depends, Query

from ..dependencies import get_record_query_service
from ..models.enums import Severity
from ..schemas.common import BillingRecord
from ..services.record_query_service import RecordQueryService


router = APIRouter()


@router.get("", response_model=dict)
async def list_records(
    upload_id: Optional[str] = None,
    severity: Optional[Severity] = Query(default=None),
    flagged_only: bool = False,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    record_query_service: RecordQueryService = Depends(get_record_query_service),
) -> dict[str, Any]:
    return record_query_service.list_records(
        upload_id=upload_id,
        severity=severity,
        flagged_only=flagged_only,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=BillingRecord)
async def get_record(
    record_id: str,
    record_query_service: RecordQueryService = Depends(get_record_query_service),
) -> BillingRecord:
    return record_query_service.get_record(record_id)

