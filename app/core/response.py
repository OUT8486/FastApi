"""统一响应封装。"""

from __future__ import annotations

from typing import Any


def success(data: Any = None, message: str = "操作成功") -> dict[str, Any]:
    return {"code": 200, "message": message, "data": data}
