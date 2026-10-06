from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import auth_guard
from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.products.repositories.products_repository import ProductsRepository
from domains.products.schemas.products_schemas import Product, ProductRegister, PaginatedProduct
from domains.products.services.products_service import ProductsService
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import AdminRequired

router = APIRouter()


def get_products_service(db: AsyncSession = Depends(get_db)) -> ProductsService:
    return ProductsService(
        ProductsRepository(db),
        InventoryRepository(db),
    )

def require_admin(current_user: Annotated[dict, Depends(auth_guard)]) -> dict:
    if current_user["role"] != UserRole.ADMIN:
        raise AdminRequired
    return current_user


@router.get("/")
def route_check():
    return {"message": "Products route"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_product(
    product_data: ProductRegister,
    _admin: Annotated[dict, Depends(require_admin)],
    products_service: ProductsService = Depends(get_products_service),

) -> None:
    await products_service.register_product(product_data)


@router.get("/all", response_model=List[Product])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    products_service: ProductsService = Depends(get_products_service),
) -> List[Product]:
    return await products_service.get_all()
    
@router.get("/category/{category}")
async def get_product_by_category(
    category: str,
    products_service: ProductsService = Depends(get_products_service)
) -> List[Product]:
    return await products_service.get_by_category(category)

@router.get("/paginated")
async def get_by_window(
    category: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
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
    