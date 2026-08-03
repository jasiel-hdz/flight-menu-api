from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings

settings = get_settings()
_DB_URL = (
    f"postgresql+psycopg2://{settings.db_username}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)
engine = create_engine(
    _DB_URL,
    pool_pre_ping=True,
    pool_size=max(1, settings.db_pool_size),
    max_overflow=max(0, settings.db_max_overflow),
    pool_timeout=max(1.0, settings.db_pool_timeout),
)
session_factory = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session, None, None]:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
