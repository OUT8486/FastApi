"""MySQL connection and query helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Sequence

import pymysql
from pymysql.cursors import DictCursor

from .config import settings


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=5,
    )


@contextmanager
def transaction() -> Iterator[pymysql.connections.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def fetch_all(sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    with transaction() as connection:
        with connection.cursor() as cursor:
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
            return list(cursor.fetchall())


def fetch_one(sql: str, params: Sequence[Any] | None = None) -> dict[str, Any] | None:
    with transaction() as connection:
        with connection.cursor() as cursor:
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
            return cursor.fetchone()


def execute(sql: str, params: Sequence[Any] | None = None) -> int:
    with transaction() as connection:
        with connection.cursor() as cursor:
            if params is None:
                return cursor.execute(sql)
            return cursor.execute(sql, params)


def execute_many(statements: Sequence[tuple[str, Sequence[Any] | None]]) -> None:
    with transaction() as connection:
        with connection.cursor() as cursor:
            for sql, params in statements:
                if params is None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, params)
