from core.exceptions import BadRequest, NotFoundError


class InventoryNotFound(NotFoundError):
    detail = "Estoque nao encontrado"

class InsufficientStock(BadRequest):
    detail = "Estoque insuficiente"