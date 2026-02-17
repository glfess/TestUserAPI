from app.api.users.router import router
from app.api.monitoring import router as monitoring_router
from app.api.handlers import app_error_handler
from app.core.exceptions import AppErrors

from fastapi import FastAPI

app = FastAPI(title="Test FastAPI",
              description="Test FastAPI",
              version="0.1.0",
              )

app.include_router(router, prefix="/api/users", tags=["users"])

app.include_router(monitoring_router)

app.add_exception_handler(AppErrors, app_error_handler)

@app.get("/")
async def root():
    return {"Session": "Online"}
