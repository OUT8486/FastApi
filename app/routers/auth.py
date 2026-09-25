"""Authentication and registration routes."""

from __future__ import annotations

import uuid

import pymysql
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from ..database import execute, fetch_one
from ..security import (
    create_access_token,
    get_current_user,
    hash_password,
    revoke_token,
    success,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])
users_router = APIRouter(prefix="/api/users", tags=["用户"])


class LoginPayload(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class RegisterPayload(BaseModel):
    user_name: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("user_name", mode="before")
    @classmethod
    def strip_user_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


@router.post("/login")
def login(payload: LoginPayload) -> dict:
    username = payload.username.strip()
    user = fetch_one(
        "SELECT user_id, user_name, password, role FROM users WHERE user_name = %s",
        (username,),
    )
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    role = user.get("role") or "用户"
    token = create_access_token(user["user_name"], user["user_id"], role)
    return success(
        {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "role": role,
            "token": token,
        },
        "登录成功",
    )


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)) -> dict:
    revoke_token(str(user["jti"]), int(user["exp"]))
    return success("退出成功")


@users_router.post("/register")
def register(payload: RegisterPayload) -> dict:
    username = payload.user_name.strip()
    if fetch_one("SELECT user_id FROM users WHERE user_name = %s", (username,)):
        raise HTTPException(status_code=409, detail="用户名已存在")

    user_id = f"U{uuid.uuid4().hex[:16]}"
    try:
        execute(
            "INSERT INTO users (user_id, user_name, password, role) VALUES (%s, %s, %s, %s)",
            (user_id, username, hash_password(payload.password), "用户"),
        )
    except pymysql.err.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="用户名已存在") from exc
    return success("注册成功")
