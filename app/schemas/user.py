from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,
                          json_schema_extra={"example": "ivan-ivanov"},
                          description="Уникальное имя пользователя"
                          )

    email: EmailStr = Field(..., min_length=6, max_length=50,
                            json_schema_extra={"example": "ivan@example.com"},
                            description="Е-мейл адрес пользователя"
                            )

class UserCreate(UserBase):
    password: str = Field(...,
                          min_length=6, max_length=24,
                          json_schema_extra={"example": "1q2w3e4r"},
                          description="Пароль пользователя"
                          )

    model_config = ConfigDict(arbitrary_types_allowed = True)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None,
                                    min_length=3,
                                    max_length=50,
                                    json_schema_extra={"example": "ivan-ivanov"},
                                    description="Новое имя пользователя"
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

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3,
                          max_length=50,
                          json_schema_extra={"example": "ivan-ivanov"},
                          description="Логин пользователя")

    password: str = Field(..., min_length=6,
                          max_length=24,
                          json_schema_extra={"example": "1q2w3e4r"},
                          description="Пароль пользователя")

class UserSchema(UserBase):
    id: int = Field(..., json_schema_extra={"example": 1},
                    description="Id пользователя в БД"
                    )
    is_active: bool = Field(..., json_schema_extra={"example": True},
                            description="Статус активации"
                            )

    is_deleted: bool = Field(..., json_schema_extra={"example": False}, description="Статус сущности")

    created_at: datetime = Field(..., json_schema_extra={"example": datetime(1970, 1, 1)},
                                 description="Дата и время регистрации"
                                 )

    model_config = ConfigDict(from_attributes = True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
