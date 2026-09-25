"""Generic CRUD routes for pharmacy resources."""

from __future__ import annotations

from decimal import Decimal

import uuid
from typing import Any

import pymysql
from fastapi import APIRouter, Body, Depends, HTTPException, Query

from ..database import execute, fetch_all, fetch_one, transaction
from ..security import get_current_user, require_admin, success

BOOLEAN_COLUMNS = {"status", "audit_status"}

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

RESOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "manufacturers": {
        "table": "manufacturer",
        "pk": "manufacturer_id",
        "prefix": "MF",
        "fields": ["manufacturer_id", "name", "credit_code"],
    },
    "drugs": {
        "table": "drug",
        "pk": "drug_id",
        "prefix": "DR",
        "fields": [
            "drug_id",
            "generic_name",
            "approval_no",
            "dosage_form",
            "specification",
            "unit",
            "purchase_price",
            "retail_price",
            "manufacturer_id",
        ],
    },
    "customers": {
        "table": "customer",
        "pk": "customer_id",
        "prefix": "CU",
        "fields": ["customer_id", "name", "type", "contact_phone"],
    },
    "suppliers": {
        "table": "supplier",
        "pk": "supplier_id",
        "prefix": "SU",
        "fields": ["supplier_id", "name", "contact_phone", "status"],
    },
    "employees": {
        "table": "employee",
        "pk": "employee_id",
        "prefix": "EM",
        "fields": ["employee_id", "name", "post"],
    },
    "warehouses": {
        "table": "warehouse",
        "pk": "warehouse_id",
        "prefix": "WH",
        "fields": ["warehouse_id", "name", "location"],
    },
    "inventory": {
        "table": "inventory",
        "pk": "inventory_id",
        "prefix": "IV",
        "fields": [
            "inventory_id",
            "drug_id",
            "warehouse_id",
            "batch_no",
            "quantity",
            "validity_date",
        ],
    },
    "purchase-orders": {
        "table": "purchaseorder",
        "pk": "po_id",
        "prefix": "PO",
        "fields": ["po_id", "supplier_id", "po_date", "employee_id", "audit_status"],
        "dependent": ("purchaseorderitem", "po_id"),
        "blocked_dependents": (
            ("warehousein", "po_id", "已有入库记录，不能删除采购订单"),
        ),
    },
    "purchase-order-items": {
        "table": "purchaseorderitem",
        "pk": "poi_id",
        "prefix": "PI",
        "fields": ["poi_id", "po_id", "drug_id", "quantity", "price"],
    },
    "sales-orders": {
        "table": "salesorder",
        "pk": "so_id",
        "prefix": "SO",
        "fields": ["so_id", "customer_id", "so_date", "employee_id"],
        "dependent": ("salesorderitem", "so_id"),
    },
    "sales-order-items": {
        "table": "salesorderitem",
        "pk": "soi_id",
        "prefix": "SI",
        "fields": ["soi_id", "so_id", "drug_id", "quantity", "price", "batch_no"],
    },
    "warehouse-in": {
        "table": "warehousein",
        "pk": "wi_id",
        "prefix": "WI",
        "fields": [
            "wi_id",
            "po_id",
            "warehouse_id",
            "in_date",
            "batch_no",
            "validity_date",
        ],
    },
}


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    for field in BOOLEAN_COLUMNS:
        if field in row and row[field] is not None:
            row[field] = bool(row[field])
    return row


def _prepare_payload(
    resource: str,
    config: dict[str, Any],
    payload: dict[str, Any],
    item_id: str | None = None,
) -> dict[str, Any]:
    allowed = set(config["fields"])
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
        data[config["pk"]] = item_id
    if not data:
        raise HTTPException(status_code=400, detail="没有可保存的字段")

    for field in REQUIRED_FIELDS.get(resource, ()):
        if item_id is None and field not in data:
            raise HTTPException(status_code=400, detail=f"{field} 不能为空")
        if field in data and data[field] is None:
            raise HTTPException(status_code=400, detail=f"{field} 不能为空")

    for field in POSITIVE_FIELDS.get(resource, ()):
        if field in data and data[field] is not None:
            try:
                numeric = Decimal(str(data[field]))
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"{field} 必须是数字") from exc
            if not numeric.is_finite() or numeric <= 0:
                raise HTTPException(status_code=400, detail=f"{field} 必须大于 0")

    for field in BOOLEAN_COLUMNS:
        if field in data and not isinstance(data[field], bool):
            raise HTTPException(status_code=400, detail=f"{field} 必须是布尔值")
    return data


def _make_router(path: str, config: dict[str, Any]) -> APIRouter:
    router = APIRouter(prefix=f"/api/{path}", tags=[path])
    table = config["table"]
    pk = config["pk"]
    prefix = config["prefix"]
    fields = config["fields"]
    dependent = config.get("dependent")
    blocked_dependents = config.get("blocked_dependents", ())

    @router.get("")
    def list_items(_user: dict[str, Any] = Depends(get_current_user)) -> dict:
        rows = fetch_all(f"SELECT * FROM `{table}` ORDER BY `{pk}`")
        return success([_normalize_row(row) for row in rows])

    @router.get("/page")
    def page_items(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        _user: dict[str, Any] = Depends(get_current_user),
    ) -> dict:
        offset = (page - 1) * size
        total_row = fetch_one(f"SELECT COUNT(*) AS total FROM `{table}`")
        rows = fetch_all(
            f"SELECT * FROM `{table}` ORDER BY `{pk}` LIMIT %s OFFSET %s",
            (size, offset),
        )
        rows = [_normalize_row(row) for row in rows]
        return success(
            {
                "list": rows,
                "total": int(total_row["total"]) if total_row else 0,
                "page": page,
                "size": size,
            }
        )

    @router.get("/{item_id}")
    def get_item(
        item_id: str,
        _user: dict[str, Any] = Depends(get_current_user),
    ) -> dict:
        row = fetch_one(
            f"SELECT * FROM `{table}` WHERE `{pk}` = %s",
            (item_id,),
        )
        if not row:
            raise HTTPException(status_code=404, detail="记录不存在")
        return success(_normalize_row(row))

    @router.post("", dependencies=[Depends(require_admin)])
    def create_item(payload: dict[str, Any] = Body(...)) -> dict:
        data = _prepare_payload(path, config, payload)
        if not data.get(pk):
            data[pk] = f"{prefix}{uuid.uuid4().hex[:16]}"
        columns = list(data.keys())
        column_sql = ", ".join(f"`{column}`" for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        try:
            execute(
                f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders})",
                tuple(data[column] for column in columns),
            )
        except (pymysql.err.IntegrityError, pymysql.err.DataError) as exc:
            raise HTTPException(status_code=400, detail="数据重复或字段值不合法") from exc
        return success(data[pk], "新增成功")

    @router.put("/{item_id}", dependencies=[Depends(require_admin)])
    def update_item(
        item_id: str,
        payload: dict[str, Any] = Body(...),
    ) -> dict:
        data = _prepare_payload(path, config, payload, item_id)
        update_fields = [field for field in fields if field != pk and field in data]
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有可更新的字段")
        assignments = ", ".join(f"`{field}` = %s" for field in update_fields)
        params = [data[field] for field in update_fields]
        params.append(item_id)
        try:
            rowcount = execute(
                f"UPDATE `{table}` SET {assignments} WHERE `{pk}` = %s",
                tuple(params),
            )
        except (pymysql.err.IntegrityError, pymysql.err.DataError) as exc:
            raise HTTPException(status_code=400, detail="数据重复或字段值不合法") from exc
        if rowcount == 0 and not fetch_one(
            f"SELECT `{pk}` FROM `{table}` WHERE `{pk}` = %s", (item_id,)
        ):
            raise HTTPException(status_code=404, detail="记录不存在")
        return success(item_id, "更新成功")

    @router.delete("/{item_id}", dependencies=[Depends(require_admin)])
    def delete_item(item_id: str) -> dict:
        try:
            with transaction() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"SELECT `{pk}` FROM `{table}` WHERE `{pk}` = %s FOR UPDATE",
                        (item_id,),
                    )
                    if not cursor.fetchone():
                        raise HTTPException(status_code=404, detail="记录不存在")

                    for blocked_table, blocked_fk, message in blocked_dependents:
                        cursor.execute(
                            f"SELECT 1 FROM `{blocked_table}` "
                            f"WHERE `{blocked_fk}` = %s LIMIT 1",
                            (item_id,),
                        )
                        if cursor.fetchone():
                            raise HTTPException(status_code=409, detail=message)

                    if dependent:
                        dependent_table, dependent_fk = dependent
                        cursor.execute(
                            f"DELETE FROM `{dependent_table}` "
                            f"WHERE `{dependent_fk}` = %s",
                            (item_id,),
                        )
                    cursor.execute(
                        f"DELETE FROM `{table}` WHERE `{pk}` = %s", (item_id,)
                    )
        except pymysql.err.IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="记录已被关联数据引用，无法删除"
            ) from exc
        return success(item_id, "删除成功")

    return router


ALL_ROUTERS = [
    _make_router(path, config) for path, config in RESOURCE_CONFIGS.items()
]
