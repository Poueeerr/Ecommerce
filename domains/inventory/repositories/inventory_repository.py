import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.inventory.models.inventory_model import InventoryModel
from domains.products.models.product_model import ProductModel


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_inventory(self, inventory: InventoryModel) -> InventoryModel:
        self.db.add(inventory)
        await self.db.flush()
        return inventory

    async def get_all(self) -> Sequence[InventoryModel]:
        result = await self.db.execute(
            select(InventoryModel).options(
                selectinload(InventoryModel.product).selectinload(ProductModel.inventory)
            )
        )
        return result.scalars().all()

    async def get_item_by_product_id(self, product_id: uuid.UUID) -> InventoryModel:
        result = await self.db.execute(
            select(InventoryModel)
            .options(selectinload(InventoryModel.product).selectinload(ProductModel.inventory))
            .where(InventoryModel.product_id == product_id)
            .with_for_update()
        )

        return result.scalars().first()

    async def add_stock(
        self,
        inventory: InventoryModel,
        quantity: int,
    ) -> InventoryModel:
        inventory.total_quantity += quantity

        await self.db.commit()

        result = await self.db.execute(
            select(InventoryModel)
            .options(selectinload(InventoryModel.product).selectinload(ProductModel.inventory))
            .where(InventoryModel.id == inventory.id)
        )
        return result.scalars().first()
