import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_returns_201_and_user(client: AsyncClient):
    response = await client.post(
        "/api/users/",
        json={
            "username": "ivan_ivanov",
            "password": "secret123",
            "email": "ivan@example.com",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "ivan_ivanov"
    assert data["email"] == "ivan@example.com"
    assert data["is_active"] is True
    assert data["is_deleted"] is False
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_user_duplicate_email_returns_400(client: AsyncClient):
    await client.post(
        "/api/users/",
        json={
            "username": "first_user",
            "password": "secret123",
            "email": "same@example.com",
        },
    )
    response = await client.post(
        "/api/users/",
        json={
            "username": "second_user",
            "password": "other456",
            "email": "same@example.com",
        },
    )
    assert response.status_code == 400
    assert "E-Mail" in response.json()["detail"] or "email" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_create_user_duplicate_username_returns_400(client: AsyncClient):
    await client.post(
        "/api/users/",
        json={
            "username": "same_name",
            "password": "secret123",
            "email": "first@example.com",
        },
    )
    response = await client.post(
        "/api/users/",
        json={
            "username": "same_name",
            "password": "other456",
            "email": "second@example.com",
        },
    )
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert (
        "именем" in detail
        or "зарегистрирован" in detail
    )


@pytest.mark.asyncio
async def test_create_user_validation_short_username_returns_422(client: AsyncClient):
    response = await client.post(
        "/api/users/",
        json={
            "username": "ab",
            "password": "secret123",
            "email": "user@example.com",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_validation_invalid_email_returns_422(client: AsyncClient):
    response = await client.post(
        "/api/users/",
        json={
            "username": "validuser",
            "password": "secret123",
            "email": "not-an-email",
        },
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_does_not_return_password(client: AsyncClient):
    response = await client.post(
        "/api/users/",
        json={"username": "testuser", "password": "testpassword", "email": "test@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert "password" not in data.get("user", {})
