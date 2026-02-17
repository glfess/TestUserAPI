class AppErrors(Exception):
    def __init__(self, message: str = "Внутренняя ошибка сервера", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EntityNotFoundError(AppErrors):
    def __init__(self, message: str = "Сущность не найдена"):
        super().__init__(message, status_code=404)

class InconsistentStateError(AppErrors):
    def __init__(self, message: str = "Нарушение логики"):
        super().__init__(message, status_code=400)

class AlreadyExistsError(AppErrors):
    def __init__(self, field: str):
        super().__init__(
            message=f"Entity with this {field} already exists",
            status_code=409
                         )
        self.field = field

class WrongDataError(AppErrors):
    def __init__(self, message: str = "Неправильный логин или пароль"):
        super().__init__(message, status_code=401)

class TooManyRequestsError(AppErrors):
    def __init__(self, message: str = "Превышен лимит"):
        super().__init__(message, status_code=429)

class TokenBlackListedError(AppErrors):
    def __init__(self, message: str = "Токен сброшен, войдите заново"):
        super().__init__(message, status_code=401)
