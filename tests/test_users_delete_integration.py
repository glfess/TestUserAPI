import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_delete_user_returns_204(client: AsyncClient):
    create = await client.post(
        "/api/users/",
        json={"username": "todel", "password": "pass1234", "email": "todel@example.com"},
    )
    assert create.status_code == 201
    user_id = create.json()["id"]
    response = await client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204
    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found_returns_404(client: AsyncClient):
    response = await client.delete("/api/users/99999")
    assert response.status_code == 404
