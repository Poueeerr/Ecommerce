import aio_pika

from core.database import SessionLocal
from domains.orders.schemas.event_schema import OrderCreatedEvent
from domains.payments.adapters.mercadopago import MercadoPagoAdapter
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.services.payments_service import PaymentsService


async def process_order_event(message: aio_pika.IncomingMessage) -> None:
    event = OrderCreatedEvent.model_validate_json(message.body)

    print(f"Processing order event: {event.model_dump()}")

    async with SessionLocal() as db, db.begin():
        payments_service = PaymentsService(
            payments_repository=PaymentsRepository(db),
            payment_adapter=MercadoPagoAdapter(),
        )
        mercado_pago_response = await payments_service.create_provider_payment(event)

    print(f"Mercado pago response: {mercado_pago_response}")
