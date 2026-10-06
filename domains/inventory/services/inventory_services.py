from typing import Sequence

from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.inventory.schemas.inventory_schema import InventorySchema


class InventoryService:
    def __init__(self, inventory_repository: InventoryRepository):
        self.inventory_repository = inventory_repository

    async def get_inventory(self) -> Sequence[InventorySchema]:
        return await self.inventory_repository.get_all() 
