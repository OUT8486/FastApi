"""业务异常定义。"""

from __future__ import annotations


class BusinessException(Exception):
    """业务异常，由全局异常处理器统一转换为标准响应体。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
