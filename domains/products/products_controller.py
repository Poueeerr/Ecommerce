from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import require_admin
from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.inventory.services.inventory_service import InventoryService
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.schemas.products_schemas import PaginatedProduct, Product, ProductRegister, ProductUpdate
from domains.products.services.product_registration_service import ProductRegistrationService
from domains.products.services.products_service import ProductsService

router = APIRouter()


def get_products_service(db: AsyncSession = Depends(get_db)) -> ProductsService:
    return ProductsService(ProductsRepository(db))


def get_product_registration_service(
    db: AsyncSession = Depends(get_db),
) -> ProductRegistrationService:
    return ProductRegistrationService(
        db,
        ProductsService(ProductsRepository(db)),
        InventoryService(InventoryRepository(db)),
    )

@router.get("/")
def route_check():
    return {"message": "Products route"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_product(
    product_data: ProductRegister,
    _admin: Annotated[dict, Depends(require_admin)],
    registration_service: ProductRegistrationService = Depends(
        get_product_registration_service
    ),

) -> None:
    await registration_service.register(product_data)


@router.get("/all", response_model=list[Product])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    products_service: ProductsService = Depends(get_products_service),
) -> list[Product]:
    return await products_service.get_all()

@router.get("/category/{category}", response_model=list[Product])
async def get_product_by_category(
    category: str,
    products_service: ProductsService = Depends(get_products_service)
) -> list[Product]:
    return await products_service.get_by_category(category)

@router.get("/paginated")
async def get_by_window(
    category: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    products_service: ProductsService = Depends(get_products_service)
)-> PaginatedProduct:
    result = await products_service.get_by_category(category, offset, limit + 1)
    has_next = len(result) > limit
    products = list(result[:limit])

    return PaginatedProduct(
        products=products,
        len_products=len(products),
        next_offset=offset + limit if has_next else None,
    )

@router.patch("/patch/{product_id}")
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    _admin: Annotated[dict, Depends(require_admin)],
    products_service: ProductsService = Depends(get_products_service)
) -> Product:
    return await products_service.edit_product(product_data, product_id)
