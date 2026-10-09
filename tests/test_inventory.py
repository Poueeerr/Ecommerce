from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from domains.inventory.inventory_exceptions import InventoryNotFound
from domains.inventory.services.inventory_service import InventoryService


def make_service():
    repository = SimpleNamespace(
        register_inventory=AsyncMock(),
        get_all=AsyncMock(),
        get_item_by_product_id=AsyncMock(),
        add_stock=AsyncMock(),
    )
    return InventoryService(repository), repository


@pytest.mark.asyncio
async def test_register_for_product_creates_empty_reservation():
    service, repository = make_service()
    product_id = uuid4()
    repository.register_inventory.side_effect = lambda inventory: inventory

    inventory = await service.register_for_product(product_id, 20)

    assert inventory.product_id == product_id
    assert inventory.total_quantity == 20
    assert inventory.reserved_quantity == 0


@pytest.mark.asyncio
async def test_add_stock_rejects_missing_inventory():
    service, repository = make_service()
    repository.get_item_by_product_id.return_value = None

    with pytest.raises(InventoryNotFound):
        await service.add_stock(uuid4(), 5)

    repository.add_stock.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_stock_delegates_existing_inventory():
    service, repository = make_service()
    inventory = object()
    repository.get_item_by_product_id.return_value = inventory
    repository.add_stock.return_value = inventory

    result = await service.add_stock(uuid4(), 5)

    assert result is inventory
    repository.add_stock.assert_awaited_once_with(inventory, 5)
