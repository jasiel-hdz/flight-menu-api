def test_health(client):
    test_client, _ = client
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
