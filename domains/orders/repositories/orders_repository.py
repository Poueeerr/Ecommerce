from sqlalchemy.ext.asyncio import AsyncSession

from domains.orders.models.orders_model import OrdersModel


class OrdersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_order(self, order: OrdersModel):
        self.db.add(order)
        await self.db.flush()
