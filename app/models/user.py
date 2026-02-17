from datetime import datetime
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, func, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(24), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint("NOT (is_active = true AND is_deleted = true) OR (is_active = false)",
                        name="check_user_active_deleted_logic"
                        ),
    )
