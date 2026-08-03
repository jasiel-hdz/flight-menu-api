from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class FlightValidateRequest(BaseModel):
    flight_number: str = Field(..., min_length=1, max_length=20)
    departure_airport: str = Field(..., min_length=3, max_length=10)
    arrival_airport: str = Field(..., min_length=3, max_length=10)


class FlightValidateResponse(BaseModel):
    valid: bool
    flight_id: uuid.UUID | None = None


class FlightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    flight_number: str
    departure_airport: str
    arrival_airport: str
    carrier: str
