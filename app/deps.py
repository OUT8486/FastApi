"""依赖注入与认证依赖（对应 Spring 的 Bean 装配 + 安全拦截器）。"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException

from .core.security import decode_access_token
from .dao import DashboardDao, TokenDao, UserDao
from .services import AuthService, DashboardService


def get_auth_service() -> AuthService:
    return AuthService(UserDao(), TokenDao())


def get_dashboard_service() -> DashboardService:
    return DashboardService(DashboardDao())


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或缺少令牌")
    token = authorization[7:].strip()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    if not payload.get("sub") or not payload.get("jti"):
        raise HTTPException(status_code=401, detail="令牌无效")
    if TokenDao().is_revoked(str(payload["jti"])):
        raise HTTPException(status_code=401, detail="令牌已注销")
    return payload


def require_admin(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    if user.get("role") not in {"管理员", "admin"}:
        raise HTTPException(status_code=403, detail="无权限执行此操作")
    return user
