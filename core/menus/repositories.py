from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from core.flights.models import Flight
from core.menus.models import Dish, Menu


class MenuRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, menu_id: uuid.UUID, *, include_deleted: bool = False) -> Menu | None:
        stmt = (
            select(Menu)
            .options(selectinload(Menu.dishes))
            .where(Menu.id == menu_id)
        )
        if not include_deleted:
            stmt = stmt.where(Menu.deleted_at.is_(None))
        return self._db.scalars(stmt).first()

    def find_duplicate(
        self,
        flight_id: uuid.UUID,
        start_date: date,
        *,
        exclude_id: uuid.UUID | None = None,
    ) -> Menu | None:
        stmt = select(Menu).where(
            Menu.flight_id == flight_id,
            Menu.start_date == start_date,
            Menu.deleted_at.is_(None),
        )
        if exclude_id is not None:
            stmt = stmt.where(Menu.id != exclude_id)
        return self._db.scalars(stmt).first()

    def list_page(
        self,
        *,
        page_number: int,
        page_size: int,
    ) -> tuple[list[Menu], int]:
        filters = [Menu.deleted_at.is_(None)]
        total = self._db.scalar(
            select(func.count()).select_from(Menu).where(*filters)
        ) or 0
        offset = (page_number - 1) * page_size
        stmt = (
            select(Menu)
            .where(*filters)
            .order_by(Menu.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(self._db.scalars(stmt).all()), total

    def search(
        self,
        *,
        flight_number: str | None,
        start_date: date | None,
        end_date: date | None,
        status: str | None,
        page_number: int,
        page_size: int,
    ) -> tuple[list[Menu], int]:
        filters = [Menu.deleted_at.is_(None)]
        stmt = select(Menu)
        count_stmt = select(func.count()).select_from(Menu)

        if flight_number:
            stmt = stmt.join(Flight, Menu.flight_id == Flight.id)
            count_stmt = count_stmt.join(Flight, Menu.flight_id == Flight.id)
            filters.append(Flight.flight_number == flight_number)
        if start_date is not None:
            filters.append(Menu.start_date >= start_date)
        if end_date is not None:
            filters.append(Menu.end_date <= end_date)
        if status is not None:
            filters.append(Menu.status == status)

        total = self._db.scalar(count_stmt.where(*filters)) or 0
        offset = (page_number - 1) * page_size
        rows = list(
            self._db.scalars(
                stmt.where(*filters)
                .order_by(Menu.created_at.desc())
                .offset(offset)
                .limit(page_size)
            ).all()
        )
        return rows, total

    def add(self, menu: Menu) -> Menu:
        self._db.add(menu)
        return menu

    def soft_delete(self, menu: Menu) -> Menu:
        menu.deleted_at = datetime.now(timezone.utc)
        menu.status = "deleted"
        return menu

    def replace_dishes(self, menu: Menu, dishes: list[Dish]) -> None:
        menu.dishes.clear()
        menu.dishes.extend(dishes)

    def add_dishes(self, menu: Menu, dishes: list[Dish]) -> None:
        menu.dishes.extend(dishes)
