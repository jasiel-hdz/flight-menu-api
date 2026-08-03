from __future__ import annotations

import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.flights.repositories import FlightRepository
from core.logging_config import get_logger
from core.menus.importers import parse_dish_upload
from core.menus.models import Dish, Menu
from core.menus.repositories import MenuRepository
from core.menus.schemas import (
    DishBulkUploadError,
    DishBulkUploadResponse,
    DishRead,
    MenuCreate,
    MenuListItem,
    MenuRead,
    MenuSearchRequest,
    MenuUpdate,
)
from core.schemas.pagination import Paginated

logger = get_logger(__name__)


class MenuService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = MenuRepository(db)
        self._flights = FlightRepository(db)

    def list_page(
        self, *, page_number: int, page_size: int
    ) -> Paginated[MenuListItem]:
        rows, total = self._repo.list_page(
            page_number=page_number, page_size=page_size
        )
        return self._paginate(rows, total, page_number, page_size, MenuListItem)

    def get(self, menu_id: uuid.UUID) -> MenuRead:
        menu = self._repo.get_by_id(menu_id)
        if menu is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu not found")
        return MenuRead.model_validate(menu)

    def create(self, payload: MenuCreate) -> Menu:
        if self._flights.get_by_id(payload.flight_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Flight not found")
        if payload.end_date < payload.start_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="end_date must be on or after start_date",
            )
        if self._repo.find_duplicate(payload.flight_id, payload.start_date):
            logger.warning(
                "menu_create_conflict",
                flight_id=str(payload.flight_id),
                start_date=str(payload.start_date),
            )
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Menu already exists for this flight and start date",
            )

        menu = Menu(
            flight_id=payload.flight_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            cycle=payload.cycle,
            status=payload.status,
            created_by=payload.created_by,
            dishes=[Dish(**dish.model_dump()) for dish in payload.dishes],
        )
        created = self._repo.add(menu)
        logger.info(
            "menu_created",
            menu_id=str(created.id),
            flight_id=str(created.flight_id),
        )
        return created

    def update(self, menu_id: uuid.UUID, payload: MenuUpdate) -> Menu:
        menu = self._repo.get_by_id(menu_id)
        if menu is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu not found")

        data = payload.model_dump(exclude_unset=True)
        dishes_data = data.pop("dishes", None)

        start_date = data.get("start_date", menu.start_date)
        end_date = data.get("end_date", menu.end_date)
        if end_date < start_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="end_date must be on or after start_date",
            )
        if "start_date" in data:
            dup = self._repo.find_duplicate(
                menu.flight_id, data["start_date"], exclude_id=menu.id
            )
            if dup is not None:
                logger.warning(
                    "menu_update_conflict",
                    menu_id=str(menu_id),
                    start_date=str(data["start_date"]),
                )
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="Menu already exists for this flight and start date",
                )

        for key, value in data.items():
            setattr(menu, key, value)

        if dishes_data is not None:
            self._repo.replace_dishes(
                menu, [Dish(**item) for item in dishes_data]
            )

        logger.info("menu_updated", menu_id=str(menu.id))
        return menu

    def soft_delete(self, menu_id: uuid.UUID) -> None:
        menu = self._repo.get_by_id(menu_id)
        if menu is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu not found")
        self._repo.soft_delete(menu)
        logger.info("menu_soft_deleted", menu_id=str(menu_id))

    def search(self, payload: MenuSearchRequest) -> Paginated[MenuListItem]:
        rows, total = self._repo.search(
            flight_number=payload.flight_number,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status,
            page_number=payload.pageNumber,
            page_size=payload.pageSize,
        )
        return self._paginate(
            rows, total, payload.pageNumber, payload.pageSize, MenuListItem
        )

    def bulk_upload_dishes(
        self,
        menu_id: uuid.UUID,
        *,
        content: bytes,
        filename: str,
    ) -> DishBulkUploadResponse:
        menu = self._repo.get_by_id(menu_id)
        if menu is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Menu not found")

        dish_payloads, parse_errors = parse_dish_upload(content, filename)
        dishes = [Dish(**item.model_dump()) for item in dish_payloads]
        self._repo.add_dishes(menu, dishes)
        self._db.flush()

        logger.info(
            "menu_dishes_bulk_uploaded",
            menu_id=str(menu_id),
            created=len(dishes),
            failed=len(parse_errors),
            filename=filename,
        )
        return DishBulkUploadResponse(
            menu_id=menu.id,
            created=len(dishes),
            failed=len(parse_errors),
            errors=[DishBulkUploadError(**err) for err in parse_errors],
            dishes=[DishRead.model_validate(dish) for dish in dishes],
        )

    @staticmethod
    def _paginate(
        rows: list[Menu],
        total: int,
        page_number: int,
        page_size: int,
        schema: type[MenuListItem],
    ) -> Paginated[MenuListItem]:
        total_pages = math.ceil(total / page_size) if total else 0
        return Paginated[MenuListItem](
            items=[schema.model_validate(row) for row in rows],
            totalRecords=total,
            totalPages=total_pages,
            pageNumber=page_number,
            pageSize=page_size,
        )
