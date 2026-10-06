from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import require_admin
from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.inventory.schemas.inventory_schemas import InventorySchema
from domains.inventory.services.inventory_service import InventoryService

router = APIRouter()


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(
        InventoryRepository(db),
    )

@router.get("/")
def route_check():
    return {"message": "Inventory route"}

@router.get("/all", response_model=list[InventorySchema])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> list[InventorySchema]:
    return await inventory_service.get_inventory()
