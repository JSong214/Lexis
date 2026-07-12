from fastapi.testclient import TestClient


def register(client: TestClient, email: str = "learner@example.com") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 201
    return response.json()


def test_register_creates_http_only_session_and_returns_current_user(
    client: TestClient,
) -> None:
    user = register(client)

    assert user["email"] == "learner@example.com"
    assert "password" not in user
    assert "lexis_session" in client.cookies
    set_cookie = client.post(
        "/api/v1/auth/login",
        json={
            "email": "learner@example.com",
            "password": "correct-horse-battery",
        },
    ).headers["set-cookie"]
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    register(client)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "LEARNER@example.com",
            "password": "another-valid-password",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    register(client)
    client.post("/api/v1/auth/logout")

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "learner@example.com",
            "password": "wrong-password-value",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_logout_revokes_session(client: TestClient) -> None:
    register(client)

    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert "lexis_session" not in client.cookies

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_sessions_are_isolated_by_user(client: TestClient) -> None:
    first = register(client, "first@example.com")
    client.post("/api/v1/auth/logout")
    second = register(client, "second@example.com")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["id"] == second["id"]
    assert response.json()["id"] != first["id"]
