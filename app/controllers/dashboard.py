"""工作台统计接口。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..core.response import success
from ..deps import get_current_user, get_dashboard_service
from ..services import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["数据看板"])


@router.get("/stats")
def dashboard_stats(
    _user: dict[str, Any] = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> dict:
    return success(service.stats())
