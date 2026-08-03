from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.flights.models import Flight


class FlightRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, flight_id: uuid.UUID) -> Flight | None:
        return self._db.get(Flight, flight_id)

    def find_by_number_and_route(
        self,
        flight_number: str,
        departure_airport: str,
        arrival_airport: str,
    ) -> Flight | None:
        stmt = select(Flight).where(
            Flight.flight_number == flight_number,
            Flight.departure_airport == departure_airport,
            Flight.arrival_airport == arrival_airport,
        )
        return self._db.scalars(stmt).first()
