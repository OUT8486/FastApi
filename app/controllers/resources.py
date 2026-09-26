"""通用 CRUD 接口。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Query

from ..core.response import success
from ..dao import ResourceDao
from ..deps import get_current_user, require_admin
from ..models import RESOURCE_CONFIGS, ResourceMeta
from ..services import ResourceService


def _make_router(resource: str, meta: ResourceMeta) -> APIRouter:
    router = APIRouter(prefix=f"/api/{resource}", tags=[resource])
    service = ResourceService(resource, ResourceDao(meta))

    @router.get("")
    def list_items(_user: dict[str, Any] = Depends(get_current_user)) -> dict:
        return success(service.list_items())

    @router.get("/page")
    def page_items(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        _user: dict[str, Any] = Depends(get_current_user),
    ) -> dict:
        return success(service.page_items(page, size))

    @router.get("/{item_id}")
    def get_item(
        item_id: str,
        _user: dict[str, Any] = Depends(get_current_user),
    ) -> dict:
        return success(service.get_item(item_id))

    @router.post("", dependencies=[Depends(require_admin)])
    def create_item(payload: dict[str, Any] = Body(...)) -> dict:
        return success(service.create_item(payload), "新增成功")

    @router.put("/{item_id}", dependencies=[Depends(require_admin)])
    def update_item(
        item_id: str,
        payload: dict[str, Any] = Body(...),
    ) -> dict:
        return success(service.update_item(item_id, payload), "更新成功")

    @router.delete("/{item_id}", dependencies=[Depends(require_admin)])
    def delete_item(item_id: str) -> dict:
        return success(service.delete_item(item_id), "删除成功")

    return router


ALL_ROUTERS = [
    _make_router(resource, meta) for resource, meta in RESOURCE_CONFIGS.items()
]
