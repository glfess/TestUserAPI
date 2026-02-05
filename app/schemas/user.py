from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,
                          json_schema_extra={"example": "ivan-ivanov"},
                          description="Уникальное имя пользователя"
                          )

    password: str = Field(...,
                          min_length=6, max_length=24,
                          json_schema_extra={"example": "1q2w3e4r"},
                          description="Пароль пользователя"
                          )

    email: EmailStr = Field(..., min_length=6, max_length=50,
                            json_schema_extra={"example": "ivan@example.com"},
                            description="Е-мейл адрес пользователя"
                            )

    model_config = ConfigDict(arbitrary_types_allowed = True)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None,
                                    min_length=3,
                                    max_length=50,
                                    json_schema_extra={"example": "ivan-ivanov"},
                                    description="Новое имя пользователя"
                                    )

    password: Optional[str] = Field(None,min_length=6,
                                    max_length=24,
                                    json_schema_extra={"example": "1q2w3e4r"},
                                    description="Новый пароль пользователя"
                                    )

    email: Optional[EmailStr] = Field(None,
                                      json_schema_extra={"example": "ivan@example.com"},
                                      description="Новый Е-мейл адрес пользователя"
                                      )
    is_active: Optional[bool] = Field(None,
                                      json_schema_extra={"example": True},
                                      description="Новый статус активности пользователя"
                                      )

    is_deleted: Optional[bool] = Field(None, json_schema_extra={"example": False},
                                       description="Флаг мягкого удаления пользователя")

    model_config = ConfigDict(from_attributes = True)

class UserSchema(BaseModel):
    id: int = Field(..., json_schema_extra={"example": 1},
                    description="Id пользователя в БД"
                    )
    username: str = Field(..., json_schema_extra={"example": "ivan-ivanov"},
                          description="Имя пользователя в БД"
                          )
    email: EmailStr = Field(..., json_schema_extra={"example": "ivan@example"},
                       description="Е-мейл пользователя в БД"
                       )
    is_active: bool = Field(..., json_schema_extra={"example": "True"},
                            description="Статус активации"
                            )
    created_at: datetime = Field(..., json_schema_extra={"example": datetime(1970, 1, 1)},
                                 description="Дата и время регистрации"
                                 )

    is_deleted: bool = Field(..., json_schema_extra={"example": False}, description="Статус сущности")

    model_config = ConfigDict(from_attributes = True)