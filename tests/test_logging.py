from __future__ import annotations


def test_health_skips_request_id_header(client):
    test_client, _ = client
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" not in response.headers


def test_protected_route_sets_request_id(client, auth_header):
    test_client, _ = client
    response = test_client.get("/api/v1/menus", headers=auth_header)
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_incoming_request_id_is_echoed(client, auth_header):
    test_client, _ = client
    headers = {**auth_header, "X-Request-ID": "test-req-123"}
    response = test_client.get("/api/v1/menus", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-req-123"
