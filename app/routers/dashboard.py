"""Dashboard summary routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..database import fetch_one
from ..security import get_current_user, success

router = APIRouter(prefix="/api/dashboard", tags=["数据看板"])


def _count(sql: str) -> int:
    row = fetch_one(sql)
    return int(row["value"]) if row else 0


@router.get("/stats")
def dashboard_stats(
    _user: dict[str, Any] = Depends(get_current_user),
) -> dict:
    sales = fetch_one(
        "SELECT COALESCE(SUM(quantity * price), 0) AS amount FROM salesorderitem"
    )
    purchases = fetch_one(
        "SELECT COALESCE(SUM(quantity * price), 0) AS amount FROM purchaseorderitem"
    )
    return success(
        {
            "drugs": _count("SELECT COUNT(*) AS value FROM drug"),
            "customers": _count("SELECT COUNT(*) AS value FROM customer"),
            "suppliers": _count("SELECT COUNT(*) AS value FROM supplier"),
            "employees": _count("SELECT COUNT(*) AS value FROM employee"),
            "warehouses": _count("SELECT COUNT(*) AS value FROM warehouse"),
            "inventory_units": _count(
                "SELECT COALESCE(SUM(quantity), 0) AS value FROM inventory"
            ),
            "purchase_orders": _count(
                "SELECT COUNT(*) AS value FROM purchaseorder"
            ),
            "sales_orders": _count("SELECT COUNT(*) AS value FROM salesorder"),
            "low_stock_items": _count(
                "SELECT COUNT(*) AS value FROM ("
                "SELECT d.drug_id FROM drug AS d "
                "LEFT JOIN inventory AS i ON i.drug_id = d.drug_id "
                "GROUP BY d.drug_id "
                "HAVING COALESCE(SUM(i.quantity), 0) < 20"
                ") AS low_stock"
            ),
            "expiring_items": _count(
                "SELECT COUNT(*) AS value FROM inventory "
                "WHERE validity_date BETWEEN CURDATE() "
                "AND DATE_ADD(CURDATE(), INTERVAL 90 DAY)"
            ),
            "sales_amount": str(sales["amount"]) if sales else "0",
            "purchase_amount": str(purchases["amount"]) if purchases else "0",
        }
    )
