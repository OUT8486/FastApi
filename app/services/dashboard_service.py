"""工作台统计业务逻辑。"""

from __future__ import annotations

from typing import Any

from ..dao import DashboardDao


class DashboardService:
    """汇总工作台统计数据。"""

    def __init__(self, dao: DashboardDao) -> None:
        self.dao = dao

    def stats(self) -> dict[str, Any]:
        return {
            "drugs": self.dao.count("drug"),
            "customers": self.dao.count("customer"),
            "suppliers": self.dao.count("supplier"),
            "employees": self.dao.count("employee"),
            "warehouses": self.dao.count("warehouse"),
            "inventory_units": self.dao.sum_quantity("inventory"),
            "purchase_orders": self.dao.count("purchaseorder"),
            "sales_orders": self.dao.count("salesorder"),
            "low_stock_items": self.dao.count_low_stock(20),
            "expiring_items": self.dao.count_expiring(90),
            "sales_amount": str(self.dao.sum_amount("salesorderitem")),
            "purchase_amount": str(self.dao.sum_amount("purchaseorderitem")),
        }
