import uuid
from decimal import Decimal

from pydantic import BaseModel


class OrderCreatedEvent(BaseModel):
    event_id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    total: Decimal
