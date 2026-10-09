from domains.payments.repositories.payments_repository import PaymentsRepository


class PaymentsService:
    def __init__(self, payments_repository: PaymentsRepository):
        self.payments_repository = payments_repository
