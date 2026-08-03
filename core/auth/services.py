from __future__ import annotations

import hmac

from fastapi import HTTPException, status

from config import Settings
from core.auth.schemas import LoginRequest, TokenResponse
from core.auth.security import create_access_token


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def login(self, payload: LoginRequest) -> TokenResponse:
        user_ok = hmac.compare_digest(payload.username, self._settings.auth_username)
        pass_ok = hmac.compare_digest(payload.password, self._settings.auth_password)
        if not (user_ok and pass_ok):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(
            subject=payload.username,
            secret=self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
            expires_minutes=self._settings.jwt_expire_minutes,
        )
        return TokenResponse(access_token=token)
