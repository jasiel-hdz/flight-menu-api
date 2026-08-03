from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

import dependencies as deps
from core.menus.schemas import (
    MenuCreate,
    MenuListItem,
    MenuRead,
    MenuSearchRequest,
    MenuUpdate,
)
from core.menus.services import MenuService
from core.schemas.pagination import Paginated

router = APIRouter(
    tags=["menus"],
    dependencies=[Depends(deps.get_current_user)],
)


@router.get("/menus", response_model=Paginated[MenuListItem])
def list_menus(
    pageNumber: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=200),
    db: Session = Depends(deps.get_db),
) -> Paginated[MenuListItem]:
    return MenuService(db).list_page(page_number=pageNumber, page_size=pageSize)


@router.post(
    "/menus",
    response_model=MenuRead,
    status_code=status.HTTP_201_CREATED,
)
def create_menu(
    body: MenuCreate,
    db: Session = Depends(deps.get_db),
) -> MenuRead:
    menu = MenuService(db).create(body)
    db.commit()
    db.refresh(menu)
    return MenuRead.model_validate(menu)


@router.post("/menus/search", response_model=Paginated[MenuListItem])
def search_menus(
    body: MenuSearchRequest,
    db: Session = Depends(deps.get_db),
) -> Paginated[MenuListItem]:
    return MenuService(db).search(body)


@router.get("/menus/{menu_id}", response_model=MenuRead)
def get_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
) -> MenuRead:
    return MenuService(db).get(menu_id)


@router.put("/menus/{menu_id}", response_model=MenuRead)
def update_menu(
    menu_id: uuid.UUID,
    body: MenuUpdate,
    db: Session = Depends(deps.get_db),
) -> MenuRead:
    menu = MenuService(db).update(menu_id, body)
    db.commit()
    db.refresh(menu)
    return MenuRead.model_validate(menu)


@router.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
) -> Response:
    MenuService(db).soft_delete(menu_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
