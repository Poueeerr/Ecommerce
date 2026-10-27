import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.orders.models.orders_model import OrdersModel


class OrdersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_order(self, order: OrdersModel) -> None:
        self.db.add(order)
        await self.db.flush()

    async def get_by_id(
        self,
        order_id: uuid.UUID,
        lock: bool = False,
    ) -> OrdersModel | None:
        stmt = select(OrdersModel).where(
            OrdersModel.id == order_id
        )

        if lock:
            stmt = stmt.with_for_update()

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        order: OrdersModel,
    ) -> OrdersModel:
        self.db.add(order)
        await self.db.flush()
        return order