"""密码与访问令牌工具（纯计算，不依赖数据库）。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any

import bcrypt

from .config import settings

PASSWORD_PREFIX = "$bcrypt-sha256$"


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
