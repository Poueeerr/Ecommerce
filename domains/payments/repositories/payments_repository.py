import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.payments.models.payments_model import PaymentsModel


class PaymentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(
        self,
        payment: PaymentsModel,
    ) -> PaymentsModel:
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def get_by_order_id(
        self,
        order_id: uuid.UUID,
        lock: bool = False,
    ) -> PaymentsModel | None:
        stmt = select(PaymentsModel).where(
            PaymentsModel.order_id == order_id
        )

        if lock:
            stmt = stmt.with_for_update()

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> PaymentsModel | None:
        stmt = select(PaymentsModel).where(
            PaymentsModel.provider_payment_id == provider_payment_id
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        payment: PaymentsModel,
    ) -> PaymentsModel:
        self.db.add(payment)
        await self.db.flush()
        return payment