from __future__ import annotations

from fastapi import APIRouter, Depends

import dependencies as deps
from config import Settings
from core.auth.schemas import LoginRequest, TokenResponse
from core.auth.services import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    settings: Settings = Depends(deps.get_settings_dep),
) -> TokenResponse:
    return AuthService(settings).login(body)
