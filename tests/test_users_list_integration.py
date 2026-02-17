import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_list_empty_returns_200_empty_list(client: AsyncClient):
    response = await client.get("/api/users/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_user_list_returns_created_users(client: AsyncClient):
    await client.post(
        "/api/users/",
        json={"username": "alice", "password": "pass1234", "email": "alice@example.com"},
    )
    await client.post(
        "/api/users/",
        json={"username": "bob", "password": "pass5678", "email": "bob@example.com"},
    )
    response = await client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = {u["username"] for u in data}
    assert usernames == {"alice", "bob"}

@pytest.mark.asyncio
async def test_user_list_pagination_skip_limit(client: AsyncClient):
    for i in range(5):
        await client.post(
            "/api/users/",
            json={
                "username": f"user_{i}",
                "password": "pass1234",
                "email": f"user{i}@example.com",
            },
        )
    response = await client.get("/api/users/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_user_list_show_deleted(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "todelete", "password": "pass1234", "email": "del@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    await client.patch(f"/api/users/{user_id}", json={"is_deleted": True, "is_active": False})
    list_default = await client.get("/api/users/")
    assert list_default.status_code == 200
    ids_default = [u["id"] for u in list_default.json()]
    assert user_id not in ids_default
    list_deleted = await client.get("/api/users/?show_deleted=true")
    assert list_deleted.status_code == 200
    data_deleted = list_deleted.json()
    if data_deleted:
        ids_deleted = [u["id"] for u in data_deleted]
        assert user_id in ids_deleted


@pytest.mark.asyncio
async def test_user_list_show_active_false_includes_inactive(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "inactive_one", "password": "pass1234", "email": "inactive@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    await client.patch(f"/api/users/{user_id}", json={"is_deleted": True, "is_active": False})
    response = await client.get("/api/users/?show_active=false&show_deleted=true")
    assert response.status_code == 200
    ids = [u["id"] for u in response.json()]
    assert user_id in ids
