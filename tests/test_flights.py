def test_validate_flight_exists(client, auth_header, sample_flight):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/flights/validate",
        headers=auth_header,
        json={
            "flight_number": "am500",
            "departure_airport": "mex",
            "arrival_airport": "cun",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["flight_id"] == str(sample_flight)


def test_validate_flight_missing(client, auth_header):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/flights/validate",
        headers=auth_header,
        json={
            "flight_number": "XX999",
            "departure_airport": "MEX",
            "arrival_airport": "GDL",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"valid": False, "flight_id": None}


def test_validate_flight_schema(client, auth_header):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/flights/validate",
        headers=auth_header,
        json={
            "flight_number": "AM500",
            "departure_airport": "12",
            "arrival_airport": "CUN",
        },
    )
    assert response.status_code == 422


def test_validate_requires_auth(client):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/flights/validate",
        json={
            "flight_number": "AM500",
            "departure_airport": "MEX",
            "arrival_airport": "CUN",
        },
    )
    assert response.status_code == 401
