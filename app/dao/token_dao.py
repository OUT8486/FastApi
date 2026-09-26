"""令牌注销记录数据访问。"""

from __future__ import annotations

import threading
import time

from .base_dao import BaseDao


class TokenDao(BaseDao):
    """token_revocation 表数据访问对象（含按需建表）。"""

    _ready = False
    _lock = threading.Lock()

    def ensure_table(self) -> None:
        if TokenDao._ready:
            return
        with TokenDao._lock:
            if TokenDao._ready:
                return
            self.execute(
                """
                CREATE TABLE IF NOT EXISTS token_revocation (
                    jti varchar(32) NOT NULL,
                    expires_at bigint NOT NULL,
                    PRIMARY KEY (jti),
                    KEY idx_token_revocation_expires_at (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            TokenDao._ready = True

    def revoke(self, jti: str, expires_at: int) -> None:
        self.ensure_table()
        now = int(time.time())
        with self.transaction() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM token_revocation WHERE expires_at < %s", (now,)
                )
                cursor.execute(
                    "INSERT IGNORE INTO token_revocation (jti, expires_at) "
                    "VALUES (%s, %s)",
                    (jti, expires_at),
                )

    def is_revoked(self, jti: str) -> bool:
        self.ensure_table()
        row = self.fetch_one(
            "SELECT jti FROM token_revocation WHERE jti = %s AND expires_at >= %s",
            (jti, int(time.time())),
        )
        return row is not None
