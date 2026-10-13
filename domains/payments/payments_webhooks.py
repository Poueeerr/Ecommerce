from fastapi import APIRouter, Depends

from domains.payments.dependencies import get_payments_service
from domains.payments.schemas.payments_schema import PaymentWebhook
from domains.payments.services.payments_service import PaymentsService

router = APIRouter()


@router.post("/webhook/payment-update")
async def payment_update(
    payment_update_data: PaymentWebhook,
    payments_service: PaymentsService = Depends(get_payments_service),
):
    # Verificar o webhook, atualizar o pagamento e a ordem e criar o shipping.
    return {"message": "Payment atualizado"}
