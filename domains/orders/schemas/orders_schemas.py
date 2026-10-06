import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from domains.orders.orders_enums import OrderStatus

class _FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrderItem(_FromModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal


class Order(_FromModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total: Decimal
    status: OrderStatus
    order_items: list[OrderItem]
    created_at: datetime
    updated_at: datetime

