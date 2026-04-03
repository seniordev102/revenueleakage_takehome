from __future__ import annotations

from functools import lru_cache

from .agents.leakage_agent import LeakageAnalysisAgent
from .repositories.analysis_repository import AnalysisRepository
from .repositories.record_repository import RecordRepository
from .repositories.upload_repository import UploadRepository
from .services.analysis_query_service import AnalysisQueryService
from .services.dashboard_query_service import DashboardQueryService
from .services.dynamodb_service import DynamoDBService
from .services.ingestion_service import IngestionService
from .services.processing_service import ProcessingService
from .services.record_query_service import RecordQueryService
from .services.runtime_dynamo import runtime_dynamo_client
from .stores.runtime_store import RuntimeStore


@lru_cache(maxsize=1)
def get_runtime_store() -> RuntimeStore:
    return RuntimeStore()


@lru_cache(maxsize=1)
def get_dynamo_service() -> DynamoDBService:
    return DynamoDBService(table_name="RevenueLeakage", client=runtime_dynamo_client)


@lru_cache(maxsize=1)
def get_upload_repository() -> UploadRepository:
    return UploadRepository(get_dynamo_service())


@lru_cache(maxsize=1)
def get_record_repository() -> RecordRepository:
    return RecordRepository(get_dynamo_service())


@lru_cache(maxsize=1)
def get_analysis_repository() -> AnalysisRepository:
    return AnalysisRepository(get_dynamo_service())


@lru_cache(maxsize=1)
def get_leakage_agent() -> LeakageAnalysisAgent:
    return LeakageAnalysisAgent(
        record_repo=get_record_repository(),
        analysis_repo=get_analysis_repository(),
    )


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService()


@lru_cache(maxsize=1)
def get_processing_service() -> ProcessingService:
    return ProcessingService(
        upload_repo=get_upload_repository(),
        record_repo=get_record_repository(),
        analysis_repo=get_analysis_repository(),
        analysis_agent=get_leakage_agent(),
        store=get_runtime_store(),
    )


@lru_cache(maxsize=1)
def get_record_query_service() -> RecordQueryService:
    return RecordQueryService(get_runtime_store())


@lru_cache(maxsize=1)
def get_analysis_query_service() -> AnalysisQueryService:
    return AnalysisQueryService(get_runtime_store())


@lru_cache(maxsize=1)
def get_dashboard_query_service() -> DashboardQueryService:
    return DashboardQueryService(get_runtime_store())
