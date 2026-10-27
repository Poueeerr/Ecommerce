from fastapi import HTTPException, Request
from mercadopago.webhook import (
    WebhookSignatureValidator,
    InvalidWebhookSignatureError,
)

from core.config import settings


def validate_mercadopago_signature(request: Request) -> None:
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")
    data_id = (
        request.query_params.get("data.id")
    )

    try:
        WebhookSignatureValidator.validate(
            x_signature,
            x_request_id,
            data_id,
            settings.MERCADO_PAGO_WEBHOOK_SECRET,
        )
        
    except InvalidWebhookSignatureError as exc:
        print("Falha na validação:", repr(exc))
        raise HTTPException(
            status_code=401,
            detail="Assinatura inválida",
        ) from exc