from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import auth_guard
from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.inventory.schemas.inventory_schema import InventorySchema
from domains.inventory.services.inventory_services import InventoryService
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import AdminRequired

router = APIRouter()


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(
        InventoryRepository(db),
    )

def require_admin(current_user: Annotated[dict, Depends(auth_guard)]) -> dict:
    if current_user["role"] != UserRole.ADMIN:
        raise AdminRequired
    return current_user


@router.get("/")
def route_check():
    return {"message": "Inventory route"}

@router.get("/all", response_model=List[InventorySchema])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> List[InventorySchema]:
    return await inventory_service.get_inventory()
    