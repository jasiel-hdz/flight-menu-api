from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from config import Settings, get_settings
from core.auth.schemas import CurrentUser
from core.auth.security import TokenError, decode_access_token
from database import get_session

http_bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_settings_dep() -> Settings:
    return get_settings()


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Security(http_bearer),
    settings: Settings = Depends(get_settings_dep),
) -> CurrentUser:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(
            token=creds.credentials,
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
    except TokenError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    if not subject or not isinstance(subject, str):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(username=subject)
