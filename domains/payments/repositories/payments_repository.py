from sqlalchemy.ext.asyncio import AsyncSession

from domains.payments.models.payments_model import PaymentsModel


class PaymentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment: PaymentsModel) -> PaymentsModel:
        self.db.add(payment)
        await self.db.flush()
        return payment
