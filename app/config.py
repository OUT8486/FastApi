"""Application settings loaded from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "药店管理系统")
        self.app_host = os.getenv("APP_HOST", "127.0.0.1")
        self.app_port = _env_int("APP_PORT", 8000)
        self.db_host = os.getenv("DB_HOST", "127.0.0.1")
        self.db_port = _env_int("DB_PORT", 3306)
        self.db_user = os.getenv("DB_USER", "root")
        self.db_password = os.getenv("DB_PASSWORD", "123456")
        self.db_name = os.getenv("DB_NAME", "medicine")
        jwt_secret = os.getenv("JWT_SECRET", "").strip()
        if (
            len(jwt_secret.encode("utf-8")) < 32
            or jwt_secret.startswith(("change-this", "replace-with"))
        ):
            raise RuntimeError(
                "JWT_SECRET 必须是至少 32 字节的随机值，请在 .env 中配置"
            )
        self.jwt_secret = jwt_secret
        self.jwt_expire_seconds = _env_int("JWT_EXPIRE_SECONDS", 86400)
        self.cors_origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        )


settings = Settings()
