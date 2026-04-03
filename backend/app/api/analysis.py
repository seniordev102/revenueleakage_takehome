from typing import List

from fastapi import APIRouter, Depends

from ..dependencies import get_analysis_query_service
from ..schemas.common import AnalysisResult
from ..services.analysis_query_service import AnalysisQueryService


router = APIRouter()


@router.get("/records/{record_id}/analysis", response_model=List[AnalysisResult])
async def get_record_analysis(
    record_id: str,
    analysis_query_service: AnalysisQueryService = Depends(get_analysis_query_service),
) -> List[AnalysisResult]:
    return analysis_query_service.get_record_analysis(record_id)

