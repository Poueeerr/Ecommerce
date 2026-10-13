import asyncio
import uuid

from domains.orders.schemas.event_schema import OrderCreatedEvent
from domains.payments.adapters.mercadopago import MercadoPagoAdapter
from domains.payments.models.payments_model import PaymentsModel
from domains.payments.payments_enums import PaymentsStatus
from domains.payments.repositories.payments_repository import PaymentsRepository


class PaymentsService:
    def __init__(
        self,
        payments_repository: PaymentsRepository,
        payment_adapter: MercadoPagoAdapter | None = None,
    ):
        self.payments_repository = payments_repository
        self.payment_adapter = payment_adapter

    async def create_provider_payment(self, event: OrderCreatedEvent) -> dict:
        if self.payment_adapter is None:
            raise RuntimeError("Adapter de pagamento não configurado")

        payment = await self.payments_repository.get_by_order_id(
            event.order_id,
            lock=True,
        )
        if payment is None:
            raise ValueError(f"Pagamento não encontrado para o pedido {event.order_id}")

        if payment.provider_preference_id:
            return {
                "provider_preference_id": payment.provider_preference_id,
                "checkout_url": payment.checkout_url,
            }

        provider_payment = await asyncio.to_thread(
            self.payment_adapter.create_payment,
            order_id=str(event.order_id),
            amount=event.total,
            email=event.email,
        )
        payment.provider_preference_id = provider_payment["provider_preference_id"]
        payment.checkout_url = provider_payment["checkout_url"]
        payment.provider = "mercado_pago"
        payment.status = PaymentsStatus.PENDING
        return provider_payment

    async def update_from_provider(
        self,
        order_id: uuid.UUID,
        provider_payment_id: str,
        status: PaymentsStatus = PaymentsStatus.PENDING,
    ) -> PaymentsModel:
        payment = await self.payments_repository.get_by_order_id(order_id)
        if payment is None:
            raise ValueError(f"Pagamento não encontrado para o pedido {order_id}")

        payment.provider_payment_id = provider_payment_id
        payment.status = status
        return payment

    async def get_checkout(self, order_id: uuid.UUID) -> PaymentsModel:
        payment = await self.payments_repository.get_by_order_id(order_id)
        if payment is None:
            raise ValueError(f"Pagamento não encontrado para o pedido {order_id}")
        return payment
