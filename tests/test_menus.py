from datetime import date, timedelta
from uuid import uuid4


def _menu_payload(flight_id, *, start=None, dishes=None):
    start = start or date(2026, 8, 1)
    return {
        "flight_id": str(flight_id),
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=7)).isoformat(),
        "cycle": "C1",
        "status": "active",
        "created_by": "tester",
        "dishes": dishes
        or [
            {
                "meal_code": "BF1",
                "name_es": "Huevos",
                "name_en": "Eggs",
                "description_es": "Con frijoles",
                "description_en": "With beans",
                "availability": "available",
            }
        ],
    }


def test_menus_require_auth(client):
    test_client, _ = client
    response = test_client.get("/api/v1/menus")
    assert response.status_code == 401


def test_create_list_get_menu(client, auth_header, sample_flight):
    test_client, _ = client
    create = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight),
    )
    assert create.status_code == 201, create.text
    created = create.json()
    assert created["cycle"] == "C1"
    assert len(created["dishes"]) == 1
    assert created["dishes"][0]["name_en"] == "Eggs"

    listing = test_client.get("/api/v1/menus", headers=auth_header)
    assert listing.status_code == 200
    body = listing.json()
    assert body["totalRecords"] == 1
    assert body["pageNumber"] == 1
    assert body["pageSize"] == 10
    assert body["totalPages"] == 1
    assert len(body["items"]) == 1

    detail = test_client.get(
        f"/api/v1/menus/{created['id']}", headers=auth_header
    )
    assert detail.status_code == 200
    assert detail.json()["id"] == created["id"]


def test_create_menu_unknown_flight(client, auth_header):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(uuid4()),
    )
    assert response.status_code == 404


def test_create_menu_duplicate(client, auth_header, sample_flight):
    test_client, _ = client
    payload = _menu_payload(sample_flight)
    assert (
        test_client.post("/api/v1/menus", headers=auth_header, json=payload).status_code
        == 201
    )
    duplicate = test_client.post("/api/v1/menus", headers=auth_header, json=payload)
    assert duplicate.status_code == 409


def test_create_menu_invalid_dates_schema(client, auth_header, sample_flight):
    test_client, _ = client
    payload = _menu_payload(sample_flight)
    payload["start_date"] = "2026-08-10"
    payload["end_date"] = "2026-08-01"
    response = test_client.post(
        "/api/v1/menus", headers=auth_header, json=payload
    )
    assert response.status_code == 422


def test_update_and_soft_delete(client, auth_header, sample_flight):
    test_client, _ = client
    created = test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight),
    ).json()

    updated = test_client.put(
        f"/api/v1/menus/{created['id']}",
        headers=auth_header,
        json={"cycle": "C2", "status": "draft"},
    )
    assert updated.status_code == 200
    assert updated.json()["cycle"] == "C2"
    assert updated.json()["status"] == "draft"

    deleted = test_client.delete(
        f"/api/v1/menus/{created['id']}", headers=auth_header
    )
    assert deleted.status_code == 204

    missing = test_client.get(
        f"/api/v1/menus/{created['id']}", headers=auth_header
    )
    assert missing.status_code == 404

    listing = test_client.get("/api/v1/menus", headers=auth_header)
    assert listing.json()["totalRecords"] == 0


def test_search_menus(client, auth_header, sample_flight):
    test_client, _ = client
    test_client.post(
        "/api/v1/menus",
        headers=auth_header,
        json=_menu_payload(sample_flight),
    )
    response = test_client.post(
        "/api/v1/menus/search",
        headers=auth_header,
        json={
            "flight_number": "AM500",
            "status": "active",
            "pageNumber": 1,
            "pageSize": 10,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["totalRecords"] == 1
    assert body["items"][0]["flight_id"] == str(sample_flight)


def test_get_menu_not_found(client, auth_header):
    test_client, _ = client
    response = test_client.get(
        f"/api/v1/menus/{uuid4()}", headers=auth_header
    )
    assert response.status_code == 404
