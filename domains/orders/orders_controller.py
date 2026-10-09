from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.middlewares.auth_guard import auth_guard
from core.database import get_db
from domains.inventory.repositories.inventory_repository import InventoryRepository
from domains.orders.events.order_dependencies import get_order_publisher
from domains.orders.events.order_publisher import OrderPublisher
from domains.orders.repository.orders_repository import OrdersRepository
from domains.orders.schemas.orders_schemas import CreateOrder, Order
from domains.orders.services.orders_serivce import OrdersService
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.products.repositories.products_repository import ProductsRepository

router = APIRouter()


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


@router.get("/")
def route_check():
    return {"message": "Orders route"}


@router.post("/create-order", response_model=Order)
async def create_order(
    order_data: CreateOrder,
    current_user: Annotated[dict, Depends(auth_guard)],
    order_service: OrdersService = Depends(get_order_service),
) -> Order:
    return await order_service.create_order(order_data, current_user)
