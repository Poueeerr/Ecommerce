from typing import Annotated

from fastapi import APIRouter, Depends

from api.middlewares.auth_guard import auth_guard
from domains.orders.dependencies import get_order_service
from domains.orders.schemas.orders_schemas import CreateOrder, Order
from domains.orders.services.orders_service import OrdersService

router = APIRouter()


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
