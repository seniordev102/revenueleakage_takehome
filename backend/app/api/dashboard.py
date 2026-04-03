from fastapi import APIRouter, Depends

from ..dependencies import get_dashboard_query_service
from ..schemas.common import DashboardSummary
from ..services.dashboard_query_service import DashboardQueryService


router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    dashboard_query_service: DashboardQueryService = Depends(get_dashboard_query_service),
) -> DashboardSummary:
    return dashboard_query_service.get_summary()

