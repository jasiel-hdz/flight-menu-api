from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _strip_required(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("must not be blank")
    return cleaned


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DishCreate(BaseModel):
    meal_code: str = Field(..., min_length=1, max_length=30)
    name_es: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description_es: str | None = Field(None, max_length=1000)
    description_en: str | None = Field(None, max_length=1000)
    image_url: str | None = Field(None, max_length=500)
    availability: str = Field(default="available", max_length=30)

    @field_validator("meal_code", "name_es", "name_en", "availability", mode="before")
    @classmethod
    def strip_required_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_required(value)
        return value

    @field_validator("description_es", "description_en", "image_url", mode="before")
    @classmethod
    def strip_optional_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_optional(value)
        return value


class DishUpdate(BaseModel):
    meal_code: str | None = Field(None, min_length=1, max_length=30)
    name_es: str | None = Field(None, min_length=1, max_length=255)
    name_en: str | None = Field(None, min_length=1, max_length=255)
    description_es: str | None = Field(None, max_length=1000)
    description_en: str | None = Field(None, max_length=1000)
    image_url: str | None = Field(None, max_length=500)
    availability: str | None = Field(None, max_length=30)

    @field_validator(
        "meal_code",
        "name_es",
        "name_en",
        "availability",
        "description_es",
        "description_en",
        "image_url",
        mode="before",
    )
    @classmethod
    def strip_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_optional(value)
        return value


class DishRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_id: uuid.UUID
    meal_code: str
    name_es: str
    name_en: str
    description_es: str | None
    description_en: str | None
    image_url: str | None
    availability: str


class MenuCreate(BaseModel):
    flight_id: uuid.UUID
    start_date: date
    end_date: date
    cycle: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="active", max_length=30)
    created_by: str = Field(..., min_length=1, max_length=120)
    dishes: list[DishCreate] = Field(default_factory=list)

    @field_validator("cycle", "status", "created_by", mode="before")
    @classmethod
    def strip_required_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_required(value)
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> MenuCreate:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class MenuUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    cycle: str | None = Field(None, min_length=1, max_length=50)
    status: str | None = Field(None, max_length=30)
    dishes: list[DishCreate] | None = None

    @field_validator("cycle", "status", mode="before")
    @classmethod
    def strip_optional_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_optional(value)
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> MenuUpdate:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be on or after start_date")
        return self


class MenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    flight_id: uuid.UUID
    start_date: date
    end_date: date
    cycle: str
    status: str
    created_by: str
    created_at: datetime
    deleted_at: datetime | None = None
    dishes: list[DishRead] = Field(default_factory=list)


class MenuListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    flight_id: uuid.UUID
    start_date: date
    end_date: date
    cycle: str
    status: str
    created_by: str
    created_at: datetime


class MenuSearchRequest(BaseModel):
    flight_number: str | None = Field(None, max_length=20)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(None, max_length=30)
    pageNumber: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=200)

    @field_validator("flight_number", "status", mode="before")
    @classmethod
    def strip_optional_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_optional(value)
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> MenuSearchRequest:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be on or after start_date")
        return self


class DishBulkUploadError(BaseModel):
    row: int
    detail: str


class DishBulkUploadResponse(BaseModel):
    menu_id: uuid.UUID
    created: int
    failed: int
    errors: list[DishBulkUploadError] = Field(default_factory=list)
    dishes: list[DishRead] = Field(default_factory=list)
