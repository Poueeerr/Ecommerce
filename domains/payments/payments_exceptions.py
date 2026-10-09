from core.exceptions import NotFoundError


class PaymentNotFound(NotFoundError):
    detail = "Pagamento nao encontrado"
