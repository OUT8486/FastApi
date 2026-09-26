"""认证相关的请求 DTO。"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


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
