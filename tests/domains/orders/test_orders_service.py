from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from domains.inventory.inventory_exceptions import InsufficientStock
from domains.orders.orders_enums import OrderStatus
from domains.orders.schemas.event_schema import OrderCreatedEvent
from domains.orders.services.orders_service import OrdersService
from tests.domains.inventory.factories import InventoryFactory
from tests.domains.orders.factories import OrderFactory
from tests.domains.products.factories import ProductFactory


def make_service():
    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=None)
    db = SimpleNamespace(begin=MagicMock(return_value=transaction))
    order_id = uuid4()
    orders_repository = SimpleNamespace(
        save_order=AsyncMock(side_effect=lambda order: setattr(order, "id", order_id))
    )
    product = ProductFactory.build_model()
    products_repository = SimpleNamespace(get_by_id=AsyncMock(return_value=product))
    inventory = InventoryFactory.build_model(product_id=product.id)
    inventory_repository = SimpleNamespace(get_item_by_product_id=AsyncMock(return_value=inventory))
    payment_repository = SimpleNamespace(create_payment=AsyncMock())
    publisher = SimpleNamespace(publish_order_created=AsyncMock())
    service = OrdersService(
        db,
        orders_repository,
        products_repository,
        inventory_repository,
        payment_repository,
        publisher,
    )
    return service, product, inventory, payment_repository, publisher


@pytest.mark.asyncio
async def test_create_order_reserves_stock_creates_payment_and_publishes_event():
    service, product, inventory, payment_repository, publisher = make_service()
    order_data = OrderFactory.build_create(product.id)

    order = await service.create_order(order_data, OrderFactory.build_user_context())

    assert order.total == Decimal("37.50")
    assert order.status == OrderStatus.PAYMENT_PENDING
    assert inventory.reserved_quantity == 5
    payment_repository.create_payment.assert_awaited_once()
    event = publisher.publish_order_created.call_args.args[0]
    assert isinstance(event, OrderCreatedEvent)
    assert event.order_id == order.id
    assert event.total == Decimal("37.50")


@pytest.mark.asyncio
async def test_create_order_does_not_publish_when_stock_is_insufficient():
    service, product, inventory, payment_repository, publisher = make_service()
    inventory.total_quantity = 2
    inventory.reserved_quantity = 1

    with pytest.raises(InsufficientStock):
        await service.create_order(
            OrderFactory.build_create(product.id), OrderFactory.build_user_context()
        )

    payment_repository.create_payment.assert_not_awaited()
    publisher.publish_order_created.assert_not_awaited()
