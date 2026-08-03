from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import dependencies as deps
from core.flights.schemas import FlightValidateRequest, FlightValidateResponse
from core.flights.services import FlightService

router = APIRouter(tags=["flights"])


@router.post("/flights/validate", response_model=FlightValidateResponse)
def validate_flight(
    body: FlightValidateRequest,
    db: Session = Depends(deps.get_db),
) -> FlightValidateResponse:
    return FlightService(db).validate(body)
