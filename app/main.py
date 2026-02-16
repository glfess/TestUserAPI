from app.api.users.router import router
from app.api.handlers import setup_exception_handlers

from fastapi import FastAPI

app = FastAPI(title="Test FastAPI",
              description="Test FastAPI",
              version="0.1.0",
              )

app.include_router(router, prefix="/api/users", tags=["users"])

setup_exception_handlers(app)

@app.get("/")
async def root():
    return {"Session": "Online"}
