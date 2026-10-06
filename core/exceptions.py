"""Exceções da aplicação.

São `Exception` comuns — nada de `fastapi` aqui — para que os services
possam levantá-las sem saber que existe HTTP. A tradução para resposta
HTTP acontece num único lugar: o handler registrado no `main.py`.

Cada domínio define as suas em `domains/<dominio>/<dominio>_exceptions.py`,
herdando de uma destas.
"""


class AppError(Exception):
    """Base de tudo. `status_code` e `detail` viram a resposta HTTP."""

    status_code: int = 500
    detail: str = "Erro interno"
    headers: dict[str, str] | None = None

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = 400
    detail = "Requisicao invalida"


class NotFoundError(AppError):
    status_code = 404
    detail = "Recurso nao encontrado"


class ConflictError(AppError):
    """O pedido conflita com o estado atual (ex.: email já cadastrado)."""

    status_code = 409
    detail = "Recurso ja existe"


class UnauthorizedError(AppError):
    """Não sabemos quem você é: credencial ausente, inválida ou expirada."""

    status_code = 401
    detail = "Nao autenticado"
    headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenError(AppError):
    """Sabemos quem você é, mas você não pode fazer isso."""

    status_code = 403
    detail = "Sem permissao para esta acao"
