import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user_returns_200(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "single", "password": "pass1234", "email": "single@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    response = await client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "single"
    assert data["email"] == "single@example.com"


@pytest.mark.asyncio
async def test_get_user_not_found_returns_404(client: AsyncClient):
    response = await client.get("/api/users/99999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_show_deleted_returns_200(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "deleted_get", "password": "pass1234", "email": "deleted_get@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    await client.patch(f"/api/users/{user_id}", json={"is_deleted": True})
    response = await client.get(f"/api/users/{user_id}?show_deleted=true")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["is_deleted"] is True
