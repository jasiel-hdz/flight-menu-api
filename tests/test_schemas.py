import pytest
from pydantic import ValidationError

from core.menus.schemas import MenuCreate, MenuSearchRequest
from core.schemas.pagination import Paginated
from core.menus.schemas import MenuListItem
from datetime import date
from uuid import uuid4


def test_menu_create_rejects_inverted_dates():
    with pytest.raises(ValidationError):
        MenuCreate(
            flight_id=uuid4(),
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 1),
            cycle="C1",
            created_by="tester",
        )


def test_search_rejects_inverted_dates():
    with pytest.raises(ValidationError):
        MenuSearchRequest(
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 1),
        )


def test_paginated_contract():
    page = Paginated[MenuListItem](
        items=[],
        totalRecords=0,
        totalPages=0,
        pageNumber=1,
        pageSize=10,
    )
    assert page.model_dump()["totalRecords"] == 0
