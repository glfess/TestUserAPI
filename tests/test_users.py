#WIP
if False:
    import pytest
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.schemas.user import UserCreate, UserUpdate
    from app.service import users as user_service

    @pytest.mark.asyncio
    async def test_user_list(client, db_session):
        await user_service.create_user(UserCreate(username="ivan",
                                              password="123456",
                                              email="ivan@example.com"),
                                   db_session
                                   )
        await user_service.create_user(UserCreate(username="danil",
                                              password="654321",
                                              email="danil@example.com"),
                                   db_session
                                   )

        response = await client.get("/api/users/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["username"] == "ivan"
        assert data[1]["username"] == "danil"

#не работает пока, RuntimeError
    @pytest.mark.asyncio
    async def test_user_get(client, db_session):
        user = await user_service.get_user(UserCreate(username="pavel",
                                                  password="567890",
                                                  email="pavel@example.com"),
                                       db_session
                                       )
        response = await client.get("/api/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["username"] == "pavel"

#    response = await client.get("/api/users/9999")
#    assert response.status_code == 404