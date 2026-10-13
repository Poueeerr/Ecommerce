from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.inventory.services.inventory_service import InventoryService


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(InventoryRepository(db))
