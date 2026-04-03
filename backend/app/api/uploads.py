from typing import Any, List

from fastapi import APIRouter, Depends, File, UploadFile

from ..core.exceptions import IngestionError
from ..core.logging import get_logger
from ..dependencies import get_ingestion_service, get_processing_service
from ..schemas.common import BillingRecord
from ..services.ingestion_service import IngestionService
from ..services.processing_service import ProcessingService


router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=dict)
async def create_upload(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
    processing_service: ProcessingService = Depends(get_processing_service),
) -> dict[str, Any]:
    if file.content_type not in ("text/csv", "application/json"):
        raise IngestionError("Unsupported file type. Use CSV or JSON.")

    content = await file.read()
    try:
        upload, records = service.ingest_file(
            file_name=file.filename,
            file_type="csv" if file.content_type == "text/csv" else "json",
            raw_bytes=content,
        )
    except ValueError as exc:
        raise IngestionError(str(exc)) from exc

    logger.info("Received file upload '%s' with content type '%s'", file.filename, file.content_type)
    return processing_service.process_records(upload, records)


@router.post("/records", response_model=dict)
async def ingest_records(
    records: List[BillingRecord],
    service: IngestionService = Depends(get_ingestion_service),
    processing_service: ProcessingService = Depends(get_processing_service),
) -> dict[str, Any]:
    if not records:
        raise IngestionError("At least one record is required.")

    upload, normalized_records = service.ingest_records(
        file_name="api-ingest",
        file_type="api",
        records=records,
    )
    logger.info("Received API ingestion request with %s records", len(records))
    return processing_service.process_records(upload, normalized_records)

