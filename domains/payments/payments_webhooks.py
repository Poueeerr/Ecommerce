from fastapi import APIRouter, Depends, Request

from domains.payments.services.mercadopago_webhook_service import validate_mercadopago_signature
from domains.payments.services.payments_service import PaymentsService
from domains.payments.dependencies import get_payments_service

router = APIRouter()


@router.post("/webhook/payment-update")
async def payment_update(
    request: Request,
    payments_service: PaymentsService = Depends(get_payments_service),
):
    topic = request.query_params.get("topic")
    notification_type = request.query_params.get("type")

    # Notificações antigas podem usar "topic" em vez de "type".
    event_type = notification_type or topic

    if event_type == "merchant_order":
        return {"message": "Evento merchant_order ignorado"}

    if event_type != "payment":
        return {"message": "Evento ignorado"}

    validate_mercadopago_signature(request)

    payload = await request.json()
    await payments_service.process_webhook(payload)

    return {"message": "Notificação processada"}