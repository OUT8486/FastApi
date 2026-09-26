"""通用资源业务逻辑：字段校验、编号生成与增删改查编排。"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

import pymysql

from ..core.exceptions import BusinessException
from ..dao import RecordNotFoundError, RecordReferencedError, ResourceDao
from ..models import BOOLEAN_COLUMNS

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "manufacturers": ("name",),
    "drugs": (
        "generic_name",
        "approval_no",
        "dosage_form",
        "specification",
        "unit",
        "purchase_price",
        "retail_price",
    ),
    "customers": ("name", "type"),
    "suppliers": ("name", "status"),
    "employees": ("name", "post"),
    "warehouses": ("name",),
    "inventory": (
        "drug_id",
        "warehouse_id",
        "batch_no",
        "quantity",
        "validity_date",
    ),
    "purchase-orders": (
        "supplier_id",
        "po_date",
        "employee_id",
        "audit_status",
    ),
    "purchase-order-items": ("po_id", "drug_id", "quantity", "price"),
    "sales-orders": ("customer_id", "so_date", "employee_id"),
    "sales-order-items": (
        "so_id",
        "drug_id",
        "quantity",
        "price",
        "batch_no",
    ),
    "warehouse-in": (
        "po_id",
        "warehouse_id",
        "in_date",
        "batch_no",
        "validity_date",
    ),
}

POSITIVE_FIELDS: dict[str, tuple[str, ...]] = {
    "drugs": ("purchase_price", "retail_price"),
    "inventory": ("quantity",),
    "purchase-order-items": ("quantity", "price"),
    "sales-order-items": ("quantity", "price"),
}


class ResourceService:
    """所有业务表共享的通用服务。"""

    def __init__(self, resource: str, dao: ResourceDao) -> None:
        self.resource = resource
        self.dao = dao

    def list_items(self) -> list[dict[str, Any]]:
        return self.dao.list_all()

    def page_items(self, page: int, size: int) -> dict[str, Any]:
        offset = (page - 1) * size
        rows, total = self.dao.page(size, offset)
        return {"list": rows, "total": total, "page": page, "size": size}

    def get_item(self, item_id: str) -> dict[str, Any]:
        row = self.dao.find_by_id(item_id)
        if not row:
            raise BusinessException("记录不存在", 404)
        return self.dao.to_entity(row)

    def create_item(self, payload: dict[str, Any]) -> str:
        data = self._prepare_payload(payload)
        pk = self.dao.pk
        if not data.get(pk):
            data[pk] = f"{self.dao.prefix}{uuid.uuid4().hex[:16]}"
        try:
            self.dao.insert(data)
        except (pymysql.err.IntegrityError, pymysql.err.DataError) as exc:
            raise BusinessException("数据重复或字段值不合法", 400) from exc
        return str(data[pk])

    def update_item(self, item_id: str, payload: dict[str, Any]) -> str:
        data = self._prepare_payload(payload, item_id)
        if not self._update_fields(data):
            raise BusinessException("没有可更新的字段", 400)
        try:
            rowcount = self.dao.update(item_id, data)
        except (pymysql.err.IntegrityError, pymysql.err.DataError) as exc:
            raise BusinessException("数据重复或字段值不合法", 400) from exc
        if rowcount == 0 and not self.dao.find_by_id(item_id):
            raise BusinessException("记录不存在", 404)
        return item_id

    def delete_item(self, item_id: str) -> str:
        try:
            self.dao.delete_with_dependents(item_id)
        except RecordNotFoundError as exc:
            raise BusinessException(str(exc), 404) from exc
        except RecordReferencedError as exc:
            raise BusinessException(str(exc), 409) from exc
        except pymysql.err.IntegrityError as exc:
            raise BusinessException("记录已被关联数据引用，无法删除", 409) from exc
        return item_id

    def _update_fields(self, data: dict[str, Any]) -> list[str]:
        pk = self.dao.pk
        return [field for field in self.dao.fields if field != pk and field in data]

    def _prepare_payload(
        self, payload: dict[str, Any], item_id: str | None = None
    ) -> dict[str, Any]:
        allowed = set(self.dao.fields)
        data: dict[str, Any] = {}
        for key, value in payload.items():
            if key not in allowed:
                continue
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    value = None
            data[key] = value

        if item_id is not None:
            data[self.dao.pk] = item_id
        if not data:
            raise BusinessException("没有可保存的字段", 400)

        for field in REQUIRED_FIELDS.get(self.resource, ()):
            if item_id is None and field not in data:
                raise BusinessException(f"{field} 不能为空", 400)
            if field in data and data[field] is None:
                raise BusinessException(f"{field} 不能为空", 400)

        for field in POSITIVE_FIELDS.get(self.resource, ()):
            if field in data and data[field] is not None:
                try:
                    numeric = Decimal(str(data[field]))
                except Exception as exc:
                    raise BusinessException(f"{field} 必须是数字", 400) from exc
                if not numeric.is_finite() or numeric <= 0:
                    raise BusinessException(f"{field} 必须大于 0", 400)

        for field in BOOLEAN_COLUMNS:
            if field in data and not isinstance(data[field], bool):
                raise BusinessException(f"{field} 必须是布尔值", 400)
        return data
