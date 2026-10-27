import asyncio
from functools import partial

import aio_pika

from core.config import settings
from core.models import load_models
from domains.orders.consumers.order_event_processor import process_order_event
from domains.orders.consumers.retry_policy import handle_failed_message
from domains.orders.orders_enums import OrderEvents

RETRY_DELAY_MS = 5_000

load_models()


async def process_order(
    message: aio_pika.IncomingMessage,
    retry_exchange: aio_pika.Exchange,
    dead_letter_exchange: aio_pika.Exchange,
) -> None:
    try:
        await process_order_event(message)
        await message.ack()
    except Exception as error:
        print(f"Consumer callback failed: {error}")

        await handle_failed_message(
            message,
            error,
            retry_exchange,
            dead_letter_exchange,
        )


async def main() -> None:
    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_CONNECTION_URL
    )

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

        await retry_queue.bind(
            retry_exchange,
            routing_key=OrderEvents.CREATED,
        )

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
