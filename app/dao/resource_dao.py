"""通用资源数据访问对象：基于表元数据完成增删改查。"""

from __future__ import annotations

from typing import Any

from ..models import BOOLEAN_COLUMNS, ResourceMeta
from .base_dao import BaseDao
from .exceptions import RecordNotFoundError, RecordReferencedError


class ResourceDao(BaseDao):
    """所有业务表通用的 Repository。"""

    def __init__(self, meta: ResourceMeta) -> None:
        self.meta = meta
        self.table: str = meta["table"]
        self.pk: str = meta["pk"]
        self.prefix: str = meta["prefix"]
        self.fields: list[str] = meta["fields"]
        self.dependent = meta.get("dependent")
        self.blocked_dependents = meta.get("blocked_dependents", ())

    def to_entity(self, row: dict[str, Any]) -> dict[str, Any]:
        """将数据库行映射为业务实体（布尔字段归一化）。"""
        for field in BOOLEAN_COLUMNS:
            if field in row and row[field] is not None:
                row[field] = bool(row[field])
        return row

    def list_all(self) -> list[dict[str, Any]]:
        rows = self.fetch_all(f"SELECT * FROM `{self.table}` ORDER BY `{self.pk}`")
        return [self.to_entity(row) for row in rows]

    def page(self, size: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        total_row = self.fetch_one(f"SELECT COUNT(*) AS total FROM `{self.table}`")
        rows = self.fetch_all(
            f"SELECT * FROM `{self.table}` ORDER BY `{self.pk}` LIMIT %s OFFSET %s",
            (size, offset),
        )
        total = int(total_row["total"]) if total_row else 0
        return [self.to_entity(row) for row in rows], total

    def find_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self.fetch_one(
            f"SELECT * FROM `{self.table}` WHERE `{self.pk}` = %s", (item_id,)
        )

    def insert(self, data: dict[str, Any]) -> None:
        columns = list(data.keys())
        column_sql = ", ".join(f"`{column}`" for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        self.execute(
            f"INSERT INTO `{self.table}` ({column_sql}) VALUES ({placeholders})",
            tuple(data[column] for column in columns),
        )

    def update(self, item_id: str, data: dict[str, Any]) -> int:
        update_fields = [
            field for field in self.fields if field != self.pk and field in data
        ]
        assignments = ", ".join(f"`{field}` = %s" for field in update_fields)
        params: list[Any] = [data[field] for field in update_fields]
        params.append(item_id)
        return self.execute(
            f"UPDATE `{self.table}` SET {assignments} WHERE `{self.pk}` = %s",
            tuple(params),
        )

    def delete_with_dependents(self, item_id: str) -> None:
        """在事务内锁定记录、校验依赖并删除（含级联子表）。"""
        with self.transaction() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT `{self.pk}` FROM `{self.table}` "
                    f"WHERE `{self.pk}` = %s FOR UPDATE",
                    (item_id,),
                )
                if not cursor.fetchone():
                    raise RecordNotFoundError("记录不存在")

                for blocked_table, blocked_fk, message in self.blocked_dependents:
                    cursor.execute(
                        f"SELECT 1 FROM `{blocked_table}` "
                        f"WHERE `{blocked_fk}` = %s LIMIT 1",
                        (item_id,),
                    )
                    if cursor.fetchone():
                        raise RecordReferencedError(message)

                if self.dependent:
                    dependent_table, dependent_fk = self.dependent
                    cursor.execute(
                        f"DELETE FROM `{dependent_table}` WHERE `{dependent_fk}` = %s",
                        (item_id,),
                    )
                cursor.execute(
                    f"DELETE FROM `{self.table}` WHERE `{self.pk}` = %s", (item_id,)
                )
