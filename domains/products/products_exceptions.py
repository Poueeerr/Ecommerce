from core.exceptions import BadRequestError, NotFoundError


class ProductNotFound(NotFoundError):
    detail = "Nenhum produto encontrado"


class ProductInvalidType(BadRequestError):
    def __init__(self, message="Categoria Inválida"):
        super().__init__(message)
