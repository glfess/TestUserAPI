import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_update_user_username_and_email_returns_200(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "oldname", "password": "pass1234", "email": "old@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    response = await client.patch(
        f"/api/users/{user_id}",
        json={"username": "newname", "email": "new@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newname"
    assert data["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_soft_delete_returns_200(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "softdel", "password": "pass1234", "email": "softdel@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    response = await client.patch(
        f"/api/users/{user_id}",
        json={"is_deleted": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_deleted"] is True
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_update_user_not_found_returns_404(client: AsyncClient):
    response = await client.patch(
        "/api/users/99999",
        json={"username": "any"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_conflict_email_returns_400(client: AsyncClient):
    await client.post(
        "/api/users/",
        json={"username": "user_a", "password": "pass1234", "email": "taken@example.com"},
    )
    create_b = await client.post(
        "/api/users/",
        json={"username": "user_b", "password": "pass1234", "email": "free@example.com"},
    )
    assert create_b.status_code == 201
    user_id_b = create_b.json()["id"]
    response = await client.patch(
        f"/api/users/{user_id_b}",
        json={"email": "taken@example.com"},
    )
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower() or "e-mail" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_user_set_active_clears_deleted(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "reactivate", "password": "pass1234", "email": "reactivate@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    await client.patch(f"/api/users/{user_id}", json={"is_deleted": True})
    response = await client.patch(f"/api/users/{user_id}", json={"is_active": True})
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert data["is_deleted"] is False


@pytest.mark.asyncio
async def test_update_user_both_active_and_deleted_normalizes(client: AsyncClient):
    """При передаче is_deleted=True и is_active=True сервис нормализует: is_deleted побеждает, is_active становится False."""
    create = await client.post(
        "/api/users/",
        json={"username": "badflags", "password": "pass1234", "email": "badflags@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    response = await client.patch(
        f"/api/users/{user_id}",
        json={"is_deleted": True, "is_active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_deleted"] is True
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_update_user_conflict_username_returns_400(client: AsyncClient):
    await client.post(
        "/api/users/",
        json={"username": "taken_username", "password": "pass1234", "email": "one@example.com"},
    )
    create_b = await client.post(
        "/api/users/",
        json={"username": "free_username", "password": "pass1234", "email": "two@example.com"},
    )
    assert create_b.status_code == 201
    user_id_b = create_b.json()["id"]
    response = await client.patch(
        f"/api/users/{user_id_b}",
        json={"username": "taken_username"},
    )
    assert response.status_code == 400
    detail = response.json().get("detail", "").lower()
    assert "username" in detail or "имя" in detail or "именем" in detail
