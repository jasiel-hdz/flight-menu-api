from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt


class TokenError(Exception):
    pass


def create_access_token(
    *,
    subject: str,
    secret: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(*, token: str, secret: str, algorithm: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.PyJWTError as exc:
        raise TokenError("invalid or expired token") from exc
