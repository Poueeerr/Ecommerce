from core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError, UnauthorizedError


class CatalogNotFound(NotFoundError):
    detail = "Nenhum produto encontrado"

class InvalidToken(UnauthorizedError):
    detail = "Token invalido ou expirado"

class AdminRequired(ForbiddenError):
    detail = "Apenas admin pode executar esta acao"

class ProductInvalidType(BadRequestError):
    def __init__(self, message="Categoria Inválida"):
        super().__init__(message)