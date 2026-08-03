from __future__ import annotations

from sqlalchemy.orm import Session

from core.flights.repositories import FlightRepository
from core.flights.schemas import FlightValidateRequest, FlightValidateResponse


class FlightService:
    def __init__(self, db: Session) -> None:
        self._repo = FlightRepository(db)

    def validate(self, payload: FlightValidateRequest) -> FlightValidateResponse:
        flight = self._repo.find_by_number_and_route(
            payload.flight_number,
            payload.departure_airport,
            payload.arrival_airport,
        )
        if flight is None:
            return FlightValidateResponse(valid=False, flight_id=None)
        return FlightValidateResponse(valid=True, flight_id=flight.id)
