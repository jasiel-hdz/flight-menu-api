"""Initial schema: flights, menus, and dishes.

Revision ID: 20260803_0001
Revises:
Create Date: 2026-08-03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260803_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "flights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("flight_number", sa.String(length=20), nullable=False),
        sa.Column("departure_airport", sa.String(length=10), nullable=False),
        sa.Column("arrival_airport", sa.String(length=10), nullable=False),
        sa.Column("carrier", sa.String(length=10), nullable=False),
    )
    op.create_index("ix_flights_flight_number", "flights", ["flight_number"])

    op.create_table(
        "menus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("flight_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("cycle", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"]),
        sa.UniqueConstraint(
            "flight_id",
            "start_date",
            name="uq_menus_flight_start_date",
        ),
    )
    op.create_index("ix_menus_flight_id", "menus", ["flight_id"])

    op.create_table(
        "dishes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("menu_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meal_code", sa.String(length=30), nullable=False),
        sa.Column("name_es", sa.String(length=255), nullable=False),
        sa.Column("name_en", sa.String(length=255), nullable=False),
        sa.Column("description_es", sa.String(length=1000), nullable=True),
        sa.Column("description_en", sa.String(length=1000), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("availability", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["menu_id"], ["menus.id"]),
    )
    op.create_index("ix_dishes_menu_id", "dishes", ["menu_id"])


def downgrade() -> None:
    op.drop_index("ix_dishes_menu_id", table_name="dishes")
    op.drop_table("dishes")
    op.drop_index("ix_menus_flight_id", table_name="menus")
    op.drop_table("menus")
    op.drop_index("ix_flights_flight_number", table_name="flights")
    op.drop_table("flights")
