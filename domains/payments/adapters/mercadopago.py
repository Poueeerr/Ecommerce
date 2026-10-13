from decimal import Decimal

from mercadopago import SDK

from core.config import settings
from domains.payments.schemas.mercadopago_schema import (
    MercadoPagoItem,
    MercadoPagoPayer,
    MercadoPagoPreference,
)


class MercadoPagoAdapter:
    def __init__(self):
        access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
        self.sdk = SDK(access_token)

    def create_payment(self, order_id: str, amount: Decimal, email: str) -> dict:
        preference = MercadoPagoPreference(
            items=[
                MercadoPagoItem(
                    id=str(order_id),
                    title=f"Pedido {order_id}",
                    quantity=1,
                    unit_price=amount,
                )
            ],
            payer=MercadoPagoPayer(
                email=email,
            ),
            external_reference=str(order_id),
            notification_url=(f"{settings.URL_BASE_ECOMM}/api/v1/payments/webhook/payment-update"),
        )

        preference_data = preference.model_dump(mode="python")
        for item in preference_data["items"]:
            item["unit_price"] = float(item["unit_price"])

        response = self.sdk.preference().create(preference_data)

        if response["status"] not in (200, 201):
            raise RuntimeError(f"Erro ao criar preferência: {response}")

        result = response["response"]

        return {
            "provider_preference_id": result["id"],
            "checkout_url": result["init_point"],
        }
