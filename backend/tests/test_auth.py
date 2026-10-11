 
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New Test User",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code in (200, 201), response.text
    body = response.json()

    assert body["email"] == "newuser@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Duplicate User",
        "password": "SecurePassword123!",
    }

    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)

    assert first.status_code in (200, 201), first.text
    assert second.status_code == 409


def test_login_success(client, create_user):
    create_user()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "clinician@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["access_token"]
    assert response.json()["token_type"].lower() == "bearer"


def test_login_invalid_password(client, create_user):
    create_user()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "clinician@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code in (400, 401)


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code in (401, 403)


def test_me_returns_authenticated_user(client, auth_headers):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["email"] == "clinician@example.com"
    assert "password_hash" not in response.json()
