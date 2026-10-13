import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from api.middlewares.auth_guard import require_admin
from domains.inventory.dependencies import get_inventory_service
from domains.inventory.schemas.inventory_schemas import InventorySchema
from domains.inventory.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/")
def route_check():
    return {"message": "Inventory route"}


@router.get("/all", response_model=list[InventorySchema])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> list[InventorySchema]:
    return await inventory_service.get_inventory()


@router.patch("/update-stock/{product_id}/ammount/{quantity}", response_model=InventorySchema)
async def update_stock(
    product_id: uuid.UUID,
    quantity: int,
    _admin: Annotated[dict, Depends(require_admin)],
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventorySchema:
    return await inventory_service.add_stock(product_id, quantity)
