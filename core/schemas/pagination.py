from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    totalRecords: int = Field(ge=0)
    totalPages: int = Field(ge=0)
    pageNumber: int = Field(ge=1)
    pageSize: int = Field(ge=1, le=200)
