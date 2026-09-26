"""用户表数据访问。"""

from __future__ import annotations

from typing import Any

from .base_dao import BaseDao


class UserDao(BaseDao):
    """users 表数据访问对象。"""

    def find_by_name(self, user_name: str) -> dict[str, Any] | None:
        return self.fetch_one(
            "SELECT user_id, user_name, password, role FROM users WHERE user_name = %s",
            (user_name,),
        )

    def exists_by_name(self, user_name: str) -> bool:
        return (
            self.fetch_one(
                "SELECT user_id FROM users WHERE user_name = %s", (user_name,)
            )
            is not None
        )

    def create(
        self, user_id: str, user_name: str, password_hash: str, role: str
    ) -> None:
        self.execute(
            "INSERT INTO users (user_id, user_name, password, role) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, user_name, password_hash, role),
        )
