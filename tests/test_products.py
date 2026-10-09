from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from domains.products.products_enums import ProductType
from domains.products.products_exceptions import ProductInvalidType, ProductNotFound
from domains.products.schemas.products_schemas import ProductCreate, ProductUpdate
from domains.products.services.products_service import ProductsService


def make_service():
    repository = SimpleNamespace(
        get_by_category=AsyncMock(),
        get_by_id=AsyncMock(),
        save_update=AsyncMock(),
        soft_delete=AsyncMock(),
        register_product=AsyncMock(),
    )
    return ProductsService(repository), repository


@pytest.mark.asyncio
async def test_get_by_category_passes_filters_to_repository():
    service, repository = make_service()
    products = [object()]
    repository.get_by_category.return_value = products

    result = await service.get_by_category(
        ProductType.CREATINE,
        offset=10,
        limit=11,
        min_price=Decimal("10.00"),
        max_price=Decimal("50.00"),
    )

    assert result == products
    repository.get_by_category.assert_awaited_once_with(
        ProductType.CREATINE, 10, 11, Decimal("10.00"), Decimal("50.00")
    )


@pytest.mark.asyncio
async def test_get_by_category_rejects_invalid_category():
    service, repository = make_service()

    with pytest.raises(ProductInvalidType):
        await service.get_by_category("invalid", 0, 10)

    repository.get_by_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_by_category_rejects_empty_result():
    service, repository = make_service()
    repository.get_by_category.return_value = []

    with pytest.raises(ProductNotFound):
        await service.get_by_category(None, 0, 10)


@pytest.mark.asyncio
async def test_edit_product_updates_only_received_fields():
    service, repository = make_service()
    product_id = uuid4()
    product = SimpleNamespace(product_name="Old", product_price=Decimal("10.00"))
    repository.get_by_id.return_value = product
    repository.save_update.return_value = product

    result = await service.edit_product(ProductUpdate(product_name="New"), product_id)

    assert result is product
    assert product.product_name == "New"
    assert product.product_price == Decimal("10.00")
    repository.save_update.assert_awaited_once_with(product)


def test_product_create_rejects_non_positive_price():
    with pytest.raises(ValueError):
        ProductCreate(
            product_name="Whey",
            product_type=ProductType.WHEY_PROTEIN,
            product_price=0,
            product_description="Protein",
        )
