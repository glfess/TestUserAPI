class AppErrors(Exception):
    pass

class EntityNotFoundError(AppErrors):
    pass

class InconsistentStateError(AppErrors):
    pass

class AlreadyExistsError(AppErrors):
    def __init__(self, field: str):
        self.field = field
