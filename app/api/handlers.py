from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import AppErrors


async def app_error_handler(request: Request, exc: AppErrors):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
                 "message": exc.message,
                 "path": request.url.path
        }
    )
