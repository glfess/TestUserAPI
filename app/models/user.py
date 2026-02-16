from datetime import datetime
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped = Column(Integer, primary_key=True)

    username: Mapped[str] = Column(String(255), nullable=False, unique=True, index=True)

    password: Mapped[str] = Column(String(255), nullable=False, server_default="")

    email: Mapped[str] = Column(String(255), nullable=False, unique=True, index=True)

    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False, server_default="false")
