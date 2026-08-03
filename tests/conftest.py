from __future__ import annotations

import os

# Must run before app/settings imports
os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AUTH_USERNAME"] = "admin"
os.environ["AUTH_PASSWORD"] = "admin"
os.environ["DEBUG"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import get_settings
from database import Base
from dependencies import get_db

get_settings.cache_clear()

from app import app  # noqa: E402
from core.flights.models import Flight  # noqa: E402
from core.menus import models as _menus_models  # noqa: F401, E402


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, SessionLocal
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_header(client):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_flight(client):
    _, SessionLocal = client
    db = SessionLocal()
    flight = Flight(
        flight_number="AM500",
        departure_airport="MEX",
        arrival_airport="CUN",
        carrier="AM",
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)
    flight_id = flight.id
    db.close()
    return flight_id
