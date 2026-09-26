"""数据访问层基类：统一封装参数化 SQL 与事务边界。"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Sequence

from ..db import database as db


class BaseDao:
    """所有 DAO 的基类，屏蔽底层数据库细节。"""

    def fetch_all(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]]:
        return db.fetch_all(sql, params)

    def fetch_one(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> dict[str, Any] | None:
        return db.fetch_one(sql, params)

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> int:
        return db.execute(sql, params)

    def execute_many(
        self, statements: Sequence[tuple[str, Sequence[Any] | None]]
    ) -> None:
        db.execute_many(statements)

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        with db.transaction() as connection:
            yield connection
