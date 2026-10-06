from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import auth_guard
from core.database import get_db
from domains.catalog.repositories.catalog_repository import CatalogRepository
from domains.catalog.schemas.catalog_schemas import CatalogProduct, CatalogRegister, PaginatedProduct
from domains.catalog.services.catalog_service import CatalogService
from domains.users.users_enums import UserRole
from domains.users.users_exceptions import AdminRequired

router = APIRouter()


def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    return CatalogService(CatalogRepository(db))

def require_admin(current_user: Annotated[dict, Depends(auth_guard)]) -> dict:
    if current_user["role"] != UserRole.ADMIN:
        raise AdminRequired
    return current_user


@router.get("/")
def route_check():
    return {"message": "Catalog route"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_product(
    product_data: CatalogRegister,
    _admin: Annotated[dict, Depends(require_admin)],
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> None:
    await catalog_service.register_product(product_data)


@router.get("/all", response_model=List[CatalogProduct])
async def get_all(
    _admin: Annotated[dict, Depends(require_admin)],
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> List[CatalogProduct]:
    return await catalog_service.get_all()
    
@router.get("/category/{category}")
async def get_product_by_category(
    category: str,
    catalog_service: CatalogService = Depends(get_catalog_service)
) -> List[CatalogProduct]:
    return await catalog_service.get_by_category(category)

@router.get("/paginated")
async def get_by_window(
    category: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    catalog_service: CatalogService = Depends(get_catalog_service)
)-> PaginatedProduct:
    result = await catalog_service.get_by_category(category, offset, limit + 1)
    has_next = len(result) > limit
    products = list(result[:limit])

    return PaginatedProduct(
        products=products,
        len_products=len(products),
        next_offset=offset + limit if has_next else None,
    )
    