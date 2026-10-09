from enum import StrEnum


class OrderStatus(StrEnum):
    PAID = "paid"
    PAYMENT_PENDING = "payment_pending"
    CANCELED = "canceled"
    COMPLETED = "completed"

class OrderEvents(StrEnum):
    CREATED = "orders.created"
