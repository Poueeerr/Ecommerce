from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.inventory.dependencies import get_inventory_service
from domains.inventory.services.inventory_service import InventoryService
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.services.product_registration_service import (
    ProductRegistrationService,
)
from domains.products.services.products_service import ProductsService


def get_products_service(db: AsyncSession = Depends(get_db)) -> ProductsService:
    return ProductsService(ProductsRepository(db))


def get_product_registration_service(
    db: AsyncSession = Depends(get_db),
    products_service: ProductsService = Depends(get_products_service),
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> ProductRegistrationService:
    return ProductRegistrationService(db, products_service, inventory_service)
