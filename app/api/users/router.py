from typing import List

from fastapi import APIRouter, Depends, Query, Path, Body
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.redis_service import RedisCacheService
from app.schemas.user import UserSchema, UserCreate, UserUpdate
from app.service.users import UserService
from app.models.user import User

from app.api.deps import get_current_user, oauth2_scheme, get_user_service
from app.core.limiter import RateLimiter

router = APIRouter()

login_limiter = RateLimiter(times=10, seconds=60)

@router.post("/logout",)
async def logout(token: str = Depends(oauth2_scheme),
                 service: UserService = Depends(get_user_service)):
    return await service.logout(token)

@router.get("/me", dependencies=[Depends(RateLimiter(times=20, seconds=60))], summary="Получить информацию о текущем пользователе")
async def read_users_me(current_user: User = Depends(get_current_user),
                        service: UserService = Depends(get_user_service)):
    return {
        "data": current_user,
        "source": "auth_context"
    }

@router.get("/", response_model=List[UserSchema],
         tags=["users"],
         summary="Выгрузка всех пользователей",
         description="""
         ### Получает список всех пользователей из БД

         Этот метод позволяет:
         - **Ограничивать выборку** через 'skip' и 'limit';
         - **Фильтр по удаленным**: по умолчанию скрыты, включаются флагом 'show_deleted'
         - **Фильтр по активным**: по умолчанию показаны, выключаются флагом 'show_active'
         """,
         responses={
             200: {"description": "Успешный возврат списка",
                   "content": {
                       "application/json": {
                           "example": [
                               {
                                   "id": 1,
                                   "username": "ivan_ivanov",
                                   "email": "ivan@example.com",
                                   "is_active": True,
                                   "is_deleted": False,
                                   "created_at": "2023-10-27T10:00:00"
                               }
                           ]
                       }
                   }
                   },
             422: {"description": "Ошибка валидции параметров"}
         })
async def user_list(skip: int = Query(0,
                                      ge=0,
                                      description="Пропустить количество пользователей"
                                      ),
                    limit: int = Query(10,
                                       ge=1, le=10,
                                       description="Лимит вывода"
                                       ),
                    show_deleted: bool = Query(False, description="Если True, покажет в том числе удаленных"),
                    show_active: bool = Query(True, description="Если False, скроет активных"),
                    service: UserService = Depends(get_user_service)
                    ):
    return await service.user_list(skip, limit, show_deleted, show_active)

@router.get("/{user_id}",
         response_model=UserSchema,
         tags=["users"],
         summary="Получить пользователя по ID",
         description="""### Получает конкретного пользователя по ID

          Этот метод позволяет:
         - **Фильтр по удаленным**: 'show_deleted' = 'True' показывает только удаленных
         - **Фильтр по активным**: 'show_active' = 'False' показывает только неактивных
          """,
         responses={
             200: {"description": "Успешный возврат пользователя",
                   "content": {
                       "application/json": {
                           "example": [
                               {
                                   "id": 1,
                                   "username": "ivan_ivanov",
                                   "email": "ivan@example.com",
                                   "is_active": True,
                                   "is_deleted": False,
                                   "created_at": "2023-10-27T10:00:00"
                               }
                           ]
                       }
                   }
                   },
             404: {"description": "Пользователи, соответствующие критериям не найдены"},
             422: {"description": "Ошибка валидции параметров"}
         })
async def get_user(user_id: int = Path(..., description="ID пользователя", ge=1),
                   show_deleted: bool = Query(False, description="Если True, покажет в том числе удаленных"),
                   show_active: bool = Query(True, description="Если False, скроет активных"),
                   service: UserService = Depends(get_user_service)
                   ):
    return await service.get_user(user_id, show_deleted, show_active)

@router.post("/",
          response_model=UserSchema,
          status_code=201,
          tags=["users"],
          summary="Создать нового пользователя",
          description="""
          ### Создание новой учетной записи пользователя.

          ***Как работает метод:***
          - Проверяется уникальность 'email' и 'username'.
          - По умолчанию создается с флагами:
            *'is_active: true'
            *'is_deleted: false'

            **Требования к данным:**
            - 'username': от 3 до 50 символов.
            - 'password': от 6 до 24 символов
            - 'email': от 6 до 50 символов
          """,
          responses={
              201: {
                  "description": "Пользователь успешно создан",
                  "content": {
                      "application/json": {
                          "example": [
                              {
                                  "id": 1,
                                  "username": "ivan_ivanov",
                                  "email": "ivan@example.com",
                                  "is_active": True,
                                  "is_deleted": False,
                                  "created_at": "2026-02-04T12:00:00"
                              }
                          ]
                      }
                  }
              },
              400: {"description": "Пользователь с таким E-Mail уже существует"},
              422: {"description": "Ошибка валидации данных (неверный формат E-Mail, "
                                   "короткий username, "
                                   "короткий пароль)."}
          })
async def create_user(data: UserCreate,
                      service: UserService = Depends(get_user_service)
                      ):
    return await service.create_user(data)

@router.patch("/{user_id}",
           response_model=UserSchema,
           summary="Обновить данные пользователя",
           description=("\n"
                        "           ### Частичное обновление данных пользователя.\n"
                        "\n"
                        "           Метод позволяет изменить информаци о пользователе. Необязательно присылать все поля - \n"
                        "           обновятся только те, что указаны\n"
                        "\n"
                        "           **Особенности:**\n"
                        "           - Если меняется 'email' или 'username', система проверит его на уникальность.\n"
                        "           - Поле 'id' и 'created_at' изменить нельзя.\n"
                        "           - Пользователь не может быть 'is_active' и 'is_deleted' одновременно, при 'is_active' = 'True', то 'is_deleted' = 'False' и наоборот'\n"
                        "           "),
           responses={
               200:
                   {
                       "description": "Пользователь успешно обновлен",
                       "content": {
                           "application/json": {
                               "example": [
                                   {
                                       "id": 1,
                                       "username": "ivan_ivanov",
                                       "email": "ivan@example.com",
                                       "is_active": True,
                                       "is_deleted": False,
                                       "created_at": "2026-02-04T12:00:00"
                                   }
                               ]
                           }
                       }
                   },
               400: {"description": "Email/username уже занят другим пользователем/"
                                    "активность и удаленность пользователя одновременно"},
               404: {"description": "Пользователь не найден"},
               422: {"description": "Ошибка валидации данных (неверный формат E-Mail, "
                                    "короткий username, "
                                    "короткий пароль)."}
           })
async def update_user(user_data: UserUpdate = Body(..., description="Данные для обновления (JSON)"),
                      user_id: int = Path(..., description="ID пользователя", ge=1),
                      service: UserService = Depends(get_user_service)
                      ):
    return await service.update_user(user_data, user_id)
#Есть Soft_delete в Patch, но в тз не указано явно какой Delete нужен
@router.delete("/{user_id}",
            status_code=204,
            summary="Полное удаление пользователя в БД",
            description="""
            **Внимание!** Этот метод безвозвратно удаляет запись из БД.
            * Используейте только если необходимо стереть данные навсегда.
            * После успешного удаления тело ответа будет пустым
            """,
            responses={
                204: {"description": "Пользователь успешно удален из системы"},
                404: {"description": "Пользователь не найден"}
            })
async def delete_user(user_id: int = Path(description="Id пользователя", ge=1),
                      service: UserService = Depends(get_user_service)
                      ):
    return await service.delete_user(user_id)

@router.post("/login",
             dependencies=[Depends(login_limiter)],
             status_code=201,
             summary="Логин пользователя",
             description="""
             ### Логин пользователя
             При успешном логине выдается токен пользователю
             """,
             responses={
                201: {"description": "Успешный вход"},
                404: {"description": "Пользователь не найден"},
                401: {"description": "Неверный логин или пароль"}
             })
async def login(data: OAuth2PasswordRequestForm = Depends(),
                service: UserService = Depends(get_user_service)):
    return await service.login(username=data.username,password=data.password)
