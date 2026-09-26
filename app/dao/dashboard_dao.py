"""看板统计所需的数据访问。"""

from __future__ import annotations

from typing import Any

from .base_dao import BaseDao


class DashboardDao(BaseDao):
    """工作台聚合查询。"""

    def count(self, table: str) -> int:
        row = self.fetch_one(f"SELECT COUNT(*) AS value FROM `{table}`")
        return int(row["value"]) if row else 0

    def sum_quantity(self, table: str) -> int:
        row = self.fetch_one(
            f"SELECT COALESCE(SUM(quantity), 0) AS value FROM `{table}`"
        )
        return int(row["value"]) if row else 0

    def sum_amount(self, table: str) -> Any:
        row = self.fetch_one(
            f"SELECT COALESCE(SUM(quantity * price), 0) AS amount FROM `{table}`"
        )
        return row["amount"] if row else 0

    def count_low_stock(self, threshold: int = 20) -> int:
        row = self.fetch_one(
            "SELECT COUNT(*) AS value FROM ("
            "SELECT d.drug_id FROM drug AS d "
            "LEFT JOIN inventory AS i ON i.drug_id = d.drug_id "
            "GROUP BY d.drug_id "
            "HAVING COALESCE(SUM(i.quantity), 0) < %s"
            ") AS low_stock",
            (threshold,),
        )
        return int(row["value"]) if row else 0

    def count_expiring(self, days: int = 90) -> int:
        row = self.fetch_one(
            "SELECT COUNT(*) AS value FROM inventory "
            "WHERE validity_date BETWEEN CURDATE() "
            "AND DATE_ADD(CURDATE(), INTERVAL %s DAY)",
            (days,),
        )
        return int(row["value"]) if row else 0
