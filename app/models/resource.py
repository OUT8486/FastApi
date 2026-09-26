"""业务资源（数据表）元数据定义。"""

from __future__ import annotations

from typing import TypedDict


class ResourceMeta(TypedDict, total=False):
    """单张业务表的元数据：表名、主键、编号前缀、字段与依赖关系。"""

    table: str
    pk: str
    prefix: str
    fields: list[str]
    dependent: tuple[str, str]
    blocked_dependents: tuple[tuple[str, str, str], ...]


BOOLEAN_COLUMNS = {"status", "audit_status"}

RESOURCE_CONFIGS: dict[str, ResourceMeta] = {
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
