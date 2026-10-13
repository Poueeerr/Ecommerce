
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.middlewares.auth_guard import require_admin
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.schemas.payment_checkout_schema import PaymentCheckoutResponse
from domains.payments.services.payments_service import PaymentsService

router = APIRouter()


def get_payments_service(db: AsyncSession = Depends(get_db)) -> PaymentsService:
    return PaymentsService(
        PaymentsRepository(db),
    )


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
