from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from config import Settings, get_settings
from database import get_session


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_settings_dep() -> Settings:
    return get_settings()
