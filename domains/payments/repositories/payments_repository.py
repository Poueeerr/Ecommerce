import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.payments.models.payments_model import PaymentsModel


class PaymentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment: PaymentsModel) -> PaymentsModel:
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def get_by_order_id(
        self,
        order_id: uuid.UUID,
        lock: bool = False,
    ) -> PaymentsModel | None:
        query = select(PaymentsModel).where(PaymentsModel.order_id == order_id)
        if lock:
            query = query.with_for_update()

        result = await self.db.execute(
            query
        )
        return result.scalar_one_or_none()
