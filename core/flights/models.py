from __future__ import annotations

import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    departure_airport: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_airport: Mapped[str] = mapped_column(String(10), nullable=False)
    carrier: Mapped[str] = mapped_column(String(10), nullable=False)

    menus = relationship("Menu", back_populates="flight")
