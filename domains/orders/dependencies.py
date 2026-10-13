from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.orders.events.order_dependencies import get_order_publisher
from domains.orders.events.order_publisher import OrderPublisher
from domains.orders.repositories.orders_repository import OrdersRepository
from domains.orders.services.orders_service import OrdersService
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.products.repositories.products_repository import ProductsRepository


async def get_order_service(
    db: AsyncSession = Depends(get_db),
    order_publisher: OrderPublisher = Depends(get_order_publisher),
) -> OrdersService:
    return OrdersService(
        db=db,
        orders_repository=OrdersRepository(db),
        products_repository=ProductsRepository(db),
        inventory_repository=InventoryRepository(db),
        payments_repository=PaymentsRepository(db),
        order_publisher=order_publisher,
    )
