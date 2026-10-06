from core.exceptions import NotFoundError


class OrderNotFound(NotFoundError):
    detail = "Pedido nao encontrado"
