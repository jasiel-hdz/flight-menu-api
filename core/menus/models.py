from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    flight_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("flights.id"), nullable=False, index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    cycle: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    flight = relationship("Flight", back_populates="menus")
    dishes = relationship("Dish", back_populates="menu", cascade="all, delete-orphan")

    # Duplicate rule: one menu per flight + start_date (active rows enforced in service)
    __table_args__ = (
        UniqueConstraint("flight_id", "start_date", name="uq_menus_flight_start_date"),
    )


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("menus.id"), nullable=False, index=True
    )
    meal_code: Mapped[str] = mapped_column(String(30), nullable=False)
    name_es: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_es: Mapped[str | None] = mapped_column(String(1000))
    description_en: Mapped[str | None] = mapped_column(String(1000))
    image_url: Mapped[str | None] = mapped_column(String(500))
    availability: Mapped[str] = mapped_column(
        String(30), nullable=False, default="available"
    )

    menu = relationship("Menu", back_populates="dishes")
