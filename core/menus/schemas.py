from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DishCreate(BaseModel):
    meal_code: str = Field(..., min_length=1, max_length=30)
    name_es: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description_es: str | None = Field(None, max_length=1000)
    description_en: str | None = Field(None, max_length=1000)
    image_url: str | None = Field(None, max_length=500)
    availability: str = Field(default="available", max_length=30)


class DishUpdate(BaseModel):
    meal_code: str | None = Field(None, min_length=1, max_length=30)
    name_es: str | None = Field(None, min_length=1, max_length=255)
    name_en: str | None = Field(None, min_length=1, max_length=255)
    description_es: str | None = Field(None, max_length=1000)
    description_en: str | None = Field(None, max_length=1000)
    image_url: str | None = Field(None, max_length=500)
    availability: str | None = Field(None, max_length=30)


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


class MenuUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    cycle: str | None = Field(None, min_length=1, max_length=50)
    status: str | None = Field(None, max_length=30)
    dishes: list[DishCreate] | None = None


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
