from app.api.users.router import router

from fastapi import FastAPI

app = FastAPI(title="Test FastAPI",
              description="Test FastAPI",
              version="0.1.0",
              )

app.include_router(router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"Session": "Online"}