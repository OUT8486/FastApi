"""数据访问层异常，供 Service 层翻译为业务异常。"""

from __future__ import annotations


class DaoError(Exception):
    """数据访问层基础异常。"""


class RecordNotFoundError(DaoError):
    """目标记录不存在。"""


class RecordReferencedError(DaoError):
    """记录被其它数据引用，无法删除。"""
