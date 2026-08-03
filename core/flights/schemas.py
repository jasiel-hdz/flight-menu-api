from __future__ import annotations

import uuid
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


_AIRPORT_RE = re.compile(r"^[A-Za-z]{3,10}$")


class FlightValidateRequest(BaseModel):
    flight_number: str = Field(..., min_length=1, max_length=20)
    departure_airport: str = Field(..., min_length=3, max_length=10)
    arrival_airport: str = Field(..., min_length=3, max_length=10)

    @field_validator("flight_number", mode="before")
    @classmethod
    def normalize_flight_number(cls, value: object) -> object:
        if isinstance(value, str):
            cleaned = value.strip().upper()
            if not cleaned:
                raise ValueError("must not be blank")
            return cleaned
        return value

    @field_validator("departure_airport", "arrival_airport", mode="before")
    @classmethod
    def normalize_airport(cls, value: object) -> object:
        if isinstance(value, str):
            cleaned = value.strip().upper()
            if not _AIRPORT_RE.fullmatch(cleaned):
                raise ValueError("must be 3-10 letters")
            return cleaned
        return value


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
