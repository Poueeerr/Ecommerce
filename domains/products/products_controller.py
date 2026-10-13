import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.middlewares.auth_guard import require_admin
from domains.products.dependencies import (
    get_product_registration_service,
    get_products_service,
)
from domains.products.schemas.products_schemas import (
    PaginatedProduct,
    Product,
    ProductRegister,
    ProductUpdate,
)
from domains.products.services.product_registration_service import ProductRegistrationService
from domains.products.services.products_service import ProductsService

router = APIRouter()


@router.get("/")
def route_check():
    return {"message": "Products route"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_product(
    product_data: ProductRegister,
    _admin: Annotated[dict, Depends(require_admin)],
    registration_service: ProductRegistrationService = Depends(get_product_registration_service),
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
    products_service: ProductsService = Depends(get_products_service),
) -> list[Product]:
    return await products_service.get_by_category(category, offset=0, limit=10)


@router.get("/paginated")
async def get_by_window(
    category: str | None = Query(None),
    min_price: Decimal | None = Query(None, gt=0, examples=[99.90]),
    max_price: Decimal | None = Query(None, gt=0, examples=[99.90]),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    products_service: ProductsService = Depends(get_products_service),
) -> PaginatedProduct:
    result = await products_service.get_by_category(
        category,
        offset,
        limit + 1,
        min_price,
        max_price,
    )
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
    products_service: ProductsService = Depends(get_products_service),
) -> Product:
    return await products_service.edit_product(product_data, product_id)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    _admin: Annotated[dict, Depends(require_admin)],
    products_service: ProductsService = Depends(get_products_service),
) -> None:
    await products_service.delete_product(product_id)
