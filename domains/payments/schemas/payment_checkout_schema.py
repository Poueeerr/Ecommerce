import uuid

from pydantic import BaseModel

from domains.payments.payments_enums import PaymentsStatus


class PaymentCheckoutResponse(BaseModel):
    order_id: uuid.UUID
    payment_status: PaymentsStatus
    checkout_url: str | None
