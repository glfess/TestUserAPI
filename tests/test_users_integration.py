import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_returns_200(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Session": "Online"}

@pytest.mark.asyncio
async def test_full_user_lifecycle(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "lifecycle", "password": "pass1234", "email": "lifecycle@example.com"},
    )
    assert create.status_code == 201
    payload = create.json()
    user_id = payload["id"]
    assert payload["username"] == "lifecycle"
    list_resp = await client.get("/api/users/")
    assert list_resp.status_code == 200
    assert any(u["id"] == user_id for u in list_resp.json())
    get_resp = await client.get(f"/api/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "lifecycle@example.com"
    patch_resp = await client.patch(
        f"/api/users/{user_id}",
        json={"username": "lifecycle_updated"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["username"] == "lifecycle_updated"
    del_resp = await client.delete(f"/api/users/{user_id}")
    assert del_resp.status_code == 204
    get_after = await client.get(f"/api/users/{user_id}")
    assert get_after.status_code == 404
