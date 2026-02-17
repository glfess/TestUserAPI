import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.error(f"База упала :({exc}")
        db_status = "error"

    return {
        "status": "alive",
        "database": db_status
    }
