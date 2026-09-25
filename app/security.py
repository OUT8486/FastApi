"""Password, token, and response helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import threading
import time
import uuid
from typing import Annotated, Any

import bcrypt
from fastapi import Depends, Header, HTTPException

from .config import settings
from .database import fetch_one, transaction


def success(data: Any = None, message: str = "操作成功") -> dict[str, Any]:
    return {"code": 200, "message": message, "data": data}


PASSWORD_PREFIX = "$bcrypt-sha256$"
_TOKEN_REVOCATION_READY = False
_TOKEN_REVOCATION_LOCK = threading.Lock()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        if password_hash.startswith(PASSWORD_PREFIX):
            digest = hashlib.sha256(password.encode("utf-8")).digest()
            return bcrypt.checkpw(
                digest, password_hash[len(PASSWORD_PREFIX) :].encode("utf-8")
            )
        if password_hash.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
    except ValueError:
        return False
    return hmac.compare_digest(password, password_hash)


def hash_password(password: str) -> str:
    # bcrypt only reads the first 72 bytes, so pre-hash long Unicode passwords first.
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt(rounds=10)).decode("utf-8")
    return f"{PASSWORD_PREFIX}{hashed}"


def _ensure_token_revocation_table() -> None:
    global _TOKEN_REVOCATION_READY
    if _TOKEN_REVOCATION_READY:
        return
    with _TOKEN_REVOCATION_LOCK:
        if _TOKEN_REVOCATION_READY:
            return
        with transaction() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS token_revocation (
                        jti varchar(32) NOT NULL,
                        expires_at bigint NOT NULL,
                        PRIMARY KEY (jti),
                        KEY idx_token_revocation_expires_at (expires_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
        _TOKEN_REVOCATION_READY = True


def revoke_token(jti: str, expires_at: int) -> None:
    _ensure_token_revocation_table()
    now = int(time.time())
    with transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM token_revocation WHERE expires_at < %s", (now,)
            )
            cursor.execute(
                "INSERT IGNORE INTO token_revocation (jti, expires_at) VALUES (%s, %s)",
                (jti, expires_at),
            )


def is_token_revoked(jti: str) -> bool:
    _ensure_token_revocation_table()
    row = fetch_one(
        "SELECT jti FROM token_revocation WHERE jti = %s AND expires_at >= %s",
        (jti, int(time.time())),
    )
    return row is not None


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(username: str, user_id: str, role: str) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + settings.jwt_expire_seconds,
        "jti": uuid.uuid4().hex,
    }
    segments = [
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
        _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
    ]
    signing_input = ".".join(segments).encode("ascii")
    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    segments.append(_b64url_encode(signature))
    return ".".join(segments)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
        signing_input = f"{header_part}.{payload_part}".encode("ascii")
        expected = hmac.new(
            settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        actual = _b64url_decode(signature_part)
        if not hmac.compare_digest(expected, actual):
            raise ValueError("签名无效")
        header = json.loads(_b64url_decode(header_part))
        if header.get("alg") != "HS256":
            raise ValueError("签名算法无效")
        payload = json.loads(_b64url_decode(payload_part))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("令牌已过期")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("令牌无效") from exc


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
    if is_token_revoked(str(payload["jti"])):
        raise HTTPException(status_code=401, detail="令牌已注销")
    return payload


def require_admin(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    if user.get("role") not in {"管理员", "admin"}:
        raise HTTPException(status_code=403, detail="无权限执行此操作")
    return user
