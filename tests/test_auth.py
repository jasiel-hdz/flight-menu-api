from core.auth.security import TokenError, create_access_token, decode_access_token


def test_login_success(client):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_invalid_credentials(client):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_validation_blank(client):
    test_client, _ = client
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "  ", "password": "admin"},
    )
    assert response.status_code == 422


def test_token_roundtrip():
    token = create_access_token(
        subject="admin",
        secret="test-secret",
        algorithm="HS256",
        expires_minutes=30,
    )
    payload = decode_access_token(
        token=token, secret="test-secret", algorithm="HS256"
    )
    assert payload["sub"] == "admin"


def test_token_invalid():
    try:
        decode_access_token(
            token="not-a-jwt", secret="test-secret", algorithm="HS256"
        )
        assert False, "expected TokenError"
    except TokenError:
        pass
