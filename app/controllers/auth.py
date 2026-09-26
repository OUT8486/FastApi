"""认证接口。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..core.response import success
from ..deps import get_auth_service, get_current_user
from ..schemas import LoginPayload, RegisterPayload
from ..services import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])
users_router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/login")
def login(
    payload: LoginPayload,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    return success(service.login(payload), "登录成功")


@router.post("/logout")
def logout(
    user: dict[str, Any] = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    service.logout(user)
    return success("退出成功")


@users_router.post("/register")
def register(
    payload: RegisterPayload,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    service.register(payload)
    return success("注册成功")
