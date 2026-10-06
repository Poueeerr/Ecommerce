from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.inventory.models.inventory_model import InventoryModel


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_inventory(self, inventory: InventoryModel) -> InventoryModel:
        self.db.add(inventory)
        await self.db.flush()
        return inventory

    async def get_all(self) -> Sequence[InventoryModel]:
        result = await self.db.execute(
            select(InventoryModel).options(selectinload(InventoryModel.product))
        )
        return result.scalars().all()
