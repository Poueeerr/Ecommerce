import asyncio
from functools import partial

import aio_pika

from core.config import settings
from core.database import SessionLocal
from core.models import load_models
from domains.orders.orders_enums import OrderEvents
from domains.orders.schemas.event_schema import OrderCreatedEvent
from domains.payments.adapters.mercadopago import MercadoPagoAdapter
from domains.payments.repositories.payments_repository import PaymentsRepository
from domains.payments.services.payments_service import PaymentsService

MAX_RETRIES = 3
RETRY_DELAY_MS = 5_000

load_models()


async def process_order(
    message: aio_pika.IncomingMessage,
    retry_exchange: aio_pika.Exchange,
    dead_letter_exchange: aio_pika.Exchange,
):
    try:
        event = OrderCreatedEvent.model_validate_json(message.body)

        print(f"Processing order event: {event.model_dump()}")

        async with SessionLocal() as db, db.begin():
            payments_service = PaymentsService(
                payments_repository=PaymentsRepository(db),
                payment_adapter=MercadoPagoAdapter(),
            )
            mercado_pago_response = await payments_service.create_provider_payment(event)

        print(f"Mercado pago response: {mercado_pago_response}")
        await message.ack()
    except Exception as error:
        await _handle_failed_message(
            message,
            error,
            retry_exchange,
            dead_letter_exchange,
        )


async def _handle_failed_message(
    message: aio_pika.IncomingMessage,
    error: Exception,
    retry_exchange: aio_pika.Exchange,
    dead_letter_exchange: aio_pika.Exchange,
) -> None:
    retry_count = int((message.headers or {}).get("x-retry-count", 0))
    print(f"Consumer callback failed (attempt {retry_count + 1}): {error}")

    if retry_count < MAX_RETRIES:
        await retry_exchange.publish(
            aio_pika.Message(
                body=message.body,
                headers={"x-retry-count": retry_count + 1},
                content_type=message.content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=OrderEvents.CREATED,
        )
    else:
        await dead_letter_exchange.publish(
            aio_pika.Message(
                body=message.body,
                headers={
                    "x-retry-count": retry_count,
                    "x-error": str(error)[:500],
                },
                content_type=message.content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=OrderEvents.CREATED,
        )

    await message.ack()


async def main():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_CONNECTION_URL)

    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            "orders",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        retry_exchange = await channel.declare_exchange(
            "orders.retry",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        dead_letter_exchange = await channel.declare_exchange(
            "orders.dlx",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(
            "order_processing",
            durable=True,
        )

        await queue.bind(
            exchange,
            routing_key=OrderEvents.CREATED,
        )

        retry_queue = await channel.declare_queue(
            "order_processing.retry",
            durable=True,
            arguments={
                "x-message-ttl": RETRY_DELAY_MS,
                "x-dead-letter-exchange": "orders",
                "x-dead-letter-routing-key": OrderEvents.CREATED,
            },
        )
        await retry_queue.bind(retry_exchange, routing_key=OrderEvents.CREATED)

        dead_letter_queue = await channel.declare_queue(
            "order_processing.dlq",
            durable=True,
        )
        await dead_letter_queue.bind(
            dead_letter_exchange,
            routing_key=OrderEvents.CREATED,
        )

        await queue.consume(
            partial(
                process_order,
                retry_exchange=retry_exchange,
                dead_letter_exchange=dead_letter_exchange,
            )
        )

        print("Waiting for order events...")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
