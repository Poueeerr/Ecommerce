import uuid
from collections.abc import Sequence

from domains.inventory.models.inventory_model import InventoryModel
from domains.inventory.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, inventory_repository: InventoryRepository):
        self.inventory_repository = inventory_repository

    async def register_for_product(
        self,
        product_id: uuid.UUID,
        quantity: int,
    ) -> InventoryModel:
        inventory = InventoryModel(
            product_id=product_id,
            quantity=quantity,
            reserved_quantity=0,
        )
        return await self.inventory_repository.register_inventory(inventory)

    async def get_inventory(self) -> Sequence[InventoryModel]:
        return await self.inventory_repository.get_all()
