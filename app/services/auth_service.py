"""认证业务逻辑：登录、注册与退出。"""

from __future__ import annotations

import uuid
from typing import Any

import pymysql

from ..core.exceptions import BusinessException
from ..core.security import create_access_token, hash_password, verify_password
from ..dao import TokenDao, UserDao
from ..schemas import LoginPayload, RegisterPayload

DEFAULT_ROLE = "用户"


class AuthService:
    """认证相关业务逻辑。"""

    def __init__(self, user_dao: UserDao, token_dao: TokenDao) -> None:
        self.user_dao = user_dao
        self.token_dao = token_dao

    def login(self, payload: LoginPayload) -> dict[str, Any]:
        username = payload.username.strip()
        user = self.user_dao.find_by_name(username)
        if not user or not verify_password(payload.password, user["password"]):
            raise BusinessException("用户名或密码错误", 401)

        role = user.get("role") or DEFAULT_ROLE
        token = create_access_token(user["user_name"], user["user_id"], role)
        return {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "role": role,
            "token": token,
        }

    def logout(self, user: dict[str, Any]) -> None:
        self.token_dao.revoke(str(user["jti"]), int(user["exp"]))

    def register(self, payload: RegisterPayload) -> None:
        username = payload.user_name.strip()
        if self.user_dao.exists_by_name(username):
            raise BusinessException("用户名已存在", 409)

        user_id = f"U{uuid.uuid4().hex[:16]}"
        try:
            self.user_dao.create(
                user_id, username, hash_password(payload.password), DEFAULT_ROLE
            )
        except pymysql.err.IntegrityError as exc:
            raise BusinessException("用户名已存在", 409) from exc
