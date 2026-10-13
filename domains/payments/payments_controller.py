import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from api.middlewares.auth_guard import require_admin
from domains.payments.dependencies import get_payments_service
from domains.payments.schemas.payment_checkout_schema import PaymentCheckoutResponse
from domains.payments.services.payments_service import PaymentsService

router = APIRouter()


@router.get("/")
def route_check():
    return {"message": "Payments"}


@router.get("/orders/{order_id}", response_model=PaymentCheckoutResponse)
async def get_order_checkout(
    _admin: Annotated[dict, Depends(require_admin)],
    order_id: uuid.UUID,
    payments_service: PaymentsService = Depends(get_payments_service),
) -> PaymentCheckoutResponse:
    payment = await payments_service.get_checkout(order_id)
    return PaymentCheckoutResponse(
        order_id=payment.order_id,
        payment_status=payment.status,
        checkout_url=payment.checkout_url,
    )
