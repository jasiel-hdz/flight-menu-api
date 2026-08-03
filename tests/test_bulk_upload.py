from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

from tests.test_menus import _menu_payload

SAMPLES = Path(__file__).resolve().parents[1] / "samples" / "dishes_sample.csv"


def test_bulk_upload_dishes_from_csv(client, auth_header, sample_flight):
    test_client, _ = client
    created = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight, dishes=[]),
    )
    assert created.status_code == 201
    menu_id = created.json()["id"]

    with SAMPLES.open("rb") as handle:
        response = test_client.post(
            f"/api/v1/menus/{menu_id}/dishes/upload",
            headers=auth_header,
            files={"file": ("dishes_sample.csv", handle, "text/csv")},
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["created"] == 4
    assert body["failed"] == 0
    assert len(body["dishes"]) == 4

    detail = test_client.get(f"/api/v1/menus/{menu_id}", headers=auth_header)
    assert detail.status_code == 200
    assert len(detail.json()["dishes"]) == 4


def test_bulk_upload_dishes_from_excel(client, auth_header, sample_flight):
    test_client, _ = client
    created = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight, dishes=[]),
    )
    menu_id = created.json()["id"]

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "meal_code",
            "name_es",
            "name_en",
            "description_es",
            "description_en",
            "image_url",
            "availability",
        ]
    )
    sheet.append(
        ["BF2", "Yogurt", "Yogurt", "Natural", "Plain", "", "available"]
    )
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = test_client.post(
        f"/api/v1/menus/{menu_id}/dishes/upload",
        headers=auth_header,
        files={
            "file": (
                "dishes.xlsx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["created"] == 1


def test_bulk_upload_rejects_bad_extension(client, auth_header, sample_flight):
    test_client, _ = client
    created = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight, dishes=[]),
    )
    menu_id = created.json()["id"]

    response = test_client.post(
        f"/api/v1/menus/{menu_id}/dishes/upload",
        headers=auth_header,
        files={"file": ("dishes.txt", b"not-a-csv", "text/plain")},
    )
    assert response.status_code == 400


def test_bulk_upload_menu_not_found(client, auth_header):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/menus/00000000-0000-0000-0000-000000000099/dishes/upload",
        headers=auth_header,
        files={"file": ("dishes_sample.csv", SAMPLES.read_bytes(), "text/csv")},
    )
    assert response.status_code == 404
