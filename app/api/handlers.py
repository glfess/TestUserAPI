from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import EntityNotFoundError, InconsistentStateError, AlreadyExistsError, AppErrors


async def app_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, EntityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
                            content={"detail": "Пользователь не найден"}
        )
    if isinstance(exc, InconsistentStateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Пользователь не может быть удаленным и активным одновременно"}
        )
    if isinstance(exc, AlreadyExistsError):
        field_map = {
            "email": "Этот E-Mail уже занят другим пользователем",
            "username": "Это имя пользователя уже занято другим пользователем"
        }
        detail = field_map.get(exc.field,
                               "Пользователь с таким E-Mail или именем пользователя уже зарегестрирован"
                               )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": detail}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )

def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppErrors, app_exception_handler)
