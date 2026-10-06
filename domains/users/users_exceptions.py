from core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError


class UserNotFound(NotFoundError):
    detail = "Usuario nao encontrado"


class EmailAlreadyRegistered(ConflictError):
    detail = "Email ja cadastrado"


class InvalidCredentials(UnauthorizedError):
    detail = "Email ou senha invalidos"


class InvalidToken(UnauthorizedError):
    detail = "Token invalido ou expirado"


class AdminRequired(ForbiddenError):
    detail = "Apenas admin pode executar esta acao"
